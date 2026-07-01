from typing import List, Optional
from datetime import date
from decimal import Decimal
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text, case
from sqlalchemy.orm import aliased
from fastapi_cache.decorator import cache
from fastapi import Request, Response

def custom_key_builder(
    func,
    namespace: Optional[str] = "",
    request: Optional[Request] = None,
    response: Optional[Response] = None,
    *args,
    **kwargs,
):
    # fastapi-cache2 passes the endpoint kwargs inside the kwargs dict under the key 'kwargs'
    endpoint_kwargs = kwargs.get("kwargs", {})
    cache_kwargs = {k: str(v) for k, v in endpoint_kwargs.items() if k != "db"}
    return f"{namespace}:{func.__module__}:{func.__name__}:{cache_kwargs}"

from app.core.database import get_db
from app.models import (
    FactDailyPrice, DimDate, DimMarket, DimRegency, 
    DimCommodity, DimMarketType
)
from app.schemas import (
    GenericResponseModel, SeasonalityData, DisparityData, 
    AnomalyData, MarketTypeSpreadData
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
async def get_seasonality(group_id: int, year: int, db: AsyncSession = Depends(get_db)):
    """
    Aggregate prices by month for time-series trends.
    """
    query = (
        select(
            DimDate.month.label("month"),
            func.avg(FactDailyPrice.price).label("avg_price")
        )
        .join(DimDate, FactDailyPrice.date_id == DimDate.date_id)
        .join(DimCommodity, FactDailyPrice.commodity_id == DimCommodity.commodity_id)
        .where(DimCommodity.group_id == group_id, DimDate.year == year)
        .group_by(DimDate.month)
        .order_by(DimDate.month)
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    data = [{"month": row.month, "avg_price": row.avg_price} for row in rows]
    return GenericResponseModel(success=True, data=data)

@router.get("/disparity", response_model=GenericResponseModel[List[DisparityData]])
@cache(expire=43200, key_builder=custom_key_builder)
async def get_disparity(date_id: date, commodity_id: int, db: AsyncSession = Depends(get_db)):
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
    
    # 2. Calculate Regional Average & Disparity
    query = (
        select(
            DimRegency.regency_id,
            DimRegency.name.label("regency_name"),
            DimRegency.latitude,
            DimRegency.longitude,
            func.avg(FactDailyPrice.price).label("regency_avg")
        )
        .select_from(FactDailyPrice)
        .join(DimMarket, FactDailyPrice.market_id == DimMarket.market_id)
        .join(DimRegency, DimMarket.regency_id == DimRegency.regency_id)
        .where(
            FactDailyPrice.date_id == target_int,
            FactDailyPrice.commodity_id == commodity_id
        )
        .group_by(DimRegency.regency_id, DimRegency.name, DimRegency.latitude, DimRegency.longitude)
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    data = []
    for row in rows:
        reg_avg = row.regency_avg
        disparity_percentage = ((reg_avg - national_avg) / national_avg) * 100
        data.append({
            "regency_id": row.regency_id,
            "regency_name": row.regency_name,
            "latitude": row.latitude,
            "longitude": row.longitude,
            "regency_avg": reg_avg,
            "national_avg": national_avg,
            "disparity_percentage": disparity_percentage
        })
        
    return GenericResponseModel(success=True, data=data)

@router.get("/anomalies", response_model=GenericResponseModel[List[AnomalyData]])
@cache(expire=43200, key_builder=custom_key_builder)
async def get_anomalies(date_id: date, db: AsyncSession = Depends(get_db)):
    """
    Early warning list tracking the Top 5 commodities exceeding their 7-day Moving Average window.
    """
    if await check_is_weekend(db, date_id):
        return GenericResponseModel(success=True, data=[])
        
    target_int = date_to_int(date_id)

    # Using raw SQL with window functions because SQLAlchemy 2.0 window functions with range/rows between 
    # require careful crafting for moving averages over specific date intervals.
    sql = text("""
        WITH DailyAvg AS (
            SELECT 
                f.commodity_id, 
                c.commodity_name as commodity_name,
                f.date_id,
                AVG(f.price) as current_price
            FROM fact_daily_prices f
            JOIN dim_commodities c ON f.commodity_id = c.commodity_id
            WHERE f.date_id <= :target_date
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

    result = await db.execute(sql, {"target_date": target_int})
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
async def get_market_type_spread(start_date: date, end_date: date, db: AsyncSession = Depends(get_db)):
    """
    Calculate structural pricing spreads between Traditional, Modern, Wholesaler, and Producer classifications.
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
            FactDailyPrice.date_id <= end_int
        )
        .group_by(DimDate.full_date, DimMarketType.name)
        .order_by(DimDate.full_date, DimMarketType.name)
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    if not rows:
        return GenericResponseModel(success=True, data=[])
        
    data = [{"date_id": row.date_id, "market_type_name": row.market_type_name, "avg_price": row.avg_price} for row in rows]
    return GenericResponseModel(success=True, data=data)
