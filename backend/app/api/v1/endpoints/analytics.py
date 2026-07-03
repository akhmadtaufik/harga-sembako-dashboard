from typing import List, Optional
from datetime import date
from decimal import Decimal
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text, case
from sqlalchemy.orm import aliased
from fastapi_cache.decorator import cache
from fastapi import Request, Response

def custom_key_builder(func, namespace: str = "", request: Request = None, response: Response = None, *args, **kwargs):
    # Extract path and query params to guarantee unique keys per filter combination
    query_string = request.url.query if request else ""
    path = request.url.path if request else ""
    return f"{namespace}:{path}:{query_string}"

from app.core.database import get_db
from app.models import (
    FactDailyPrice, DimDate, DimMarket, DimRegency, 
    DimCommodity, DimMarketType, DimProvince
)
from app.schemas import (
    GenericResponseModel, SeasonalityData, DisparityData, 
    AnomalyData, MarketTypeSpreadData, RegionalMatrixData
)

def date_to_int(d: date) -> int:
    return int(d.strftime("%Y%m%d"))

router = APIRouter()

async def check_is_weekend(db: AsyncSession, target_date: date) -> bool:
    """Helper to check if a date is a weekend."""
    target_int = date_to_int(target_date)
    result = await db.execute(select(DimDate.is_weekend).where(DimDate.date_id == target_int))
    is_weekend = result.scalar_one_or_none()
    return bool(is_weekend)

@router.get("/seasonality", response_model=GenericResponseModel[List[SeasonalityData]])
@cache(expire=43200, key_builder=custom_key_builder)
async def get_seasonality(request: Request, commodity_id: int, year: int, db: AsyncSession = Depends(get_db)):
    """
    Aggregate prices by day for time-series trends based on a specific commodity.
    """
    query = (
        select(
            DimDate.full_date.label("date_id"),
            func.avg(FactDailyPrice.price).label("avg_price")
        )
        .join(DimDate, FactDailyPrice.date_id == DimDate.date_id)
        .where(FactDailyPrice.commodity_id == commodity_id, DimDate.year == year)
        .group_by(DimDate.full_date)
        .order_by(DimDate.full_date)
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    data = [{"date_id": row.date_id, "avg_price": row.avg_price} for row in rows]
    return GenericResponseModel(success=True, data=data)

@router.get("/disparity", response_model=GenericResponseModel[List[DisparityData]])
@cache(expire=43200, key_builder=custom_key_builder)
async def get_disparity(request: Request, date_id: date, commodity_id: int, province_id: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    """
    Compare regional averages against the national baseline for the Choropleth map layer.
    """
    if await check_is_weekend(db, date_id):
        return GenericResponseModel(success=True, data=[])

    target_int = date_to_int(date_id)

    # 1. Calculate National Average
    nat_query = select(func.avg(FactDailyPrice.price)).where(
        FactDailyPrice.date_id == target_int,
        FactDailyPrice.commodity_id == commodity_id
    )
    nat_result = await db.execute(nat_query)
    national_avg = nat_result.scalar_one_or_none()

    if national_avg is None or national_avg == 0:
        return GenericResponseModel(success=True, data=[])
    
    # 2. Calculate Regional Average & Disparity using LEFT JOIN to retain structural placeholders
    aggregated_facts = (
        select(
            DimMarket.regency_id,
            func.avg(FactDailyPrice.price).label("regency_avg")
        )
        .select_from(FactDailyPrice)
        .join(DimMarket, FactDailyPrice.market_id == DimMarket.market_id)
        .where(
            FactDailyPrice.date_id == target_int,
            FactDailyPrice.commodity_id == commodity_id
        )
        .group_by(DimMarket.regency_id)
    ).subquery()

    query = (
        select(
            DimRegency.regency_id,
            DimRegency.name.label("regency_name"),
            DimProvince.province_id,
            DimProvince.name.label("province_name"),
            DimRegency.latitude,
            DimRegency.longitude,
            aggregated_facts.c.regency_avg
        )
        .select_from(DimRegency)
        .join(DimProvince, DimRegency.province_id == DimProvince.province_id)
        .outerjoin(aggregated_facts, DimRegency.regency_id == aggregated_facts.c.regency_id)
    )
    
    if province_id is not None:
        query = query.where(DimRegency.province_id == province_id)
        
    result = await db.execute(query)
    rows = result.all()
    
    data = []
    for row in rows:
        reg_avg = row.regency_avg
        if reg_avg is not None:
            disparity_percentage = ((reg_avg - national_avg) / national_avg) * 100
        else:
            disparity_percentage = 0
            
        data.append({
            "regency_id": row.regency_id,
            "regency_name": row.regency_name,
            "province_id": row.province_id,
            "province_name": row.province_name,
            "latitude": row.latitude,
            "longitude": row.longitude,
            "regency_avg": reg_avg if reg_avg is not None else 0,
            "national_avg": national_avg,
            "disparity_percentage": disparity_percentage
        })
        
    return GenericResponseModel(success=True, data=data)

@router.get("/anomalies", response_model=GenericResponseModel[List[AnomalyData]])
@cache(expire=43200, key_builder=custom_key_builder)
async def get_anomalies(request: Request, date_id: date, province_id: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    """
    Early warning list tracking the Top 5 commodities exceeding their 7-day Moving Average window.
    """
    if await check_is_weekend(db, date_id):
        return GenericResponseModel(success=True, data=[])
        
    target_int = date_to_int(date_id)

    join_clause = ""
    where_clause = ""
    params = {"target_date": target_int}
    
    if province_id is not None:
        join_clause = "JOIN dim_markets m ON f.market_id = m.market_id JOIN dim_regencies r ON m.regency_id = r.regency_id"
        where_clause = "AND r.province_id = :prov_id"
        params["prov_id"] = province_id

    # Using raw SQL with window functions because SQLAlchemy 2.0 window functions with range/rows between 
    # require careful crafting for moving averages over specific date intervals.
    sql = text(f"""
        WITH DailyAvg AS (
            SELECT 
                f.commodity_id, 
                c.commodity_name as commodity_name,
                f.date_id,
                AVG(f.price) as current_price
            FROM fact_daily_prices f
            JOIN dim_commodities c ON f.commodity_id = c.commodity_id
            {join_clause}
            WHERE f.date_id <= :target_date {where_clause}
            GROUP BY f.commodity_id, c.commodity_name, f.date_id
        ),
        MovingAvgs AS (
            SELECT 
                commodity_id,
                commodity_name,
                date_id,
                current_price,
                AVG(current_price) OVER (
                    PARTITION BY commodity_id 
                    ORDER BY date_id 
                    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
                ) as moving_average_7d
            FROM DailyAvg
        )
        SELECT 
            commodity_id,
            commodity_name,
            current_price,
            moving_average_7d,
            ((current_price - moving_average_7d) / NULLIF(moving_average_7d, 0)) * 100 as percentage_difference
        FROM MovingAvgs
        WHERE date_id = :target_date
          AND moving_average_7d > 0
          AND current_price > moving_average_7d
        ORDER BY percentage_difference DESC
        LIMIT 5;
    """)

    result = await db.execute(sql, params)
    rows = result.all()
    
    data = []
    for row in rows:
        data.append({
            "commodity_id": row.commodity_id,
            "commodity_name": row.commodity_name,
            "current_price": row.current_price,
            "moving_average_7d": row.moving_average_7d,
            "percentage_difference": row.percentage_difference
        })
        
    return GenericResponseModel(success=True, data=data)

@router.get("/spread/market-types", response_model=GenericResponseModel[List[MarketTypeSpreadData]])
@cache(expire=43200, key_builder=custom_key_builder)
async def get_market_type_spread(request: Request, start_date: date, end_date: date, commodity_id: int, province_id: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    """
    Calculate structural pricing spreads between Traditional, Modern, Wholesaler, and Producer classifications for a specific commodity.
    """
    start_int = date_to_int(start_date)
    end_int = date_to_int(end_date)
    
    query = (
        select(
            DimDate.full_date.label("date_id"),
            DimMarketType.name.label("market_type_name"),
            func.avg(FactDailyPrice.price).label("avg_price")
        )
        .join(DimDate, FactDailyPrice.date_id == DimDate.date_id)
        .join(DimMarket, FactDailyPrice.market_id == DimMarket.market_id)
        .join(DimMarketType, DimMarket.market_type_id == DimMarketType.market_type_id)
        .where(
            FactDailyPrice.date_id >= start_int,
            FactDailyPrice.date_id <= end_int,
            FactDailyPrice.commodity_id == commodity_id
        )
    )
    
    if province_id is not None:
        query = query.join(DimRegency, DimMarket.regency_id == DimRegency.regency_id).where(DimRegency.province_id == province_id)
        
    query = query.group_by(DimDate.full_date, DimMarketType.name).order_by(DimDate.full_date, DimMarketType.name)
    
    result = await db.execute(query)
    rows = result.all()
    
    if not rows:
        return GenericResponseModel(success=True, data=[])
        
    data = [{"date_id": row.date_id, "market_type_name": row.market_type_name, "avg_price": row.avg_price} for row in rows]
    return GenericResponseModel(success=True, data=data)

@router.get("/regional-matrix", response_model=GenericResponseModel[List[RegionalMatrixData]])
@cache(expire=43200, key_builder=custom_key_builder)
async def get_regional_matrix(request: Request, date_id: date, commodity_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get aggregated regional averages matrix data.
    """
    target_int = date_to_int(date_id)

    query = (
        select(
            DimProvince.province_id,
            DimProvince.name.label("province_name"),
            func.avg(FactDailyPrice.price).label("average_price"),
            func.count(FactDailyPrice.price).label("record_count")
        )
        .select_from(FactDailyPrice)
        .join(DimMarket, FactDailyPrice.market_id == DimMarket.market_id)
        .join(DimRegency, DimMarket.regency_id == DimRegency.regency_id)
        .join(DimProvince, DimRegency.province_id == DimProvince.province_id)
        .where(
            FactDailyPrice.date_id == target_int,
            FactDailyPrice.commodity_id == commodity_id
        )
        .group_by(DimProvince.province_id, DimProvince.name)
        .order_by(func.avg(FactDailyPrice.price).desc())
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    data = []
    for row in rows:
        data.append({
            "province_id": row.province_id,
            "province_name": row.province_name,
            "average_price": row.average_price,
            "record_count": row.record_count
        })
        
    return GenericResponseModel(success=True, data=data)
