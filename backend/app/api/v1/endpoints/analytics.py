from typing import List, Optional
from datetime import date, timedelta
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
    AnomalyData, MarketTypeSpreadData, RegionalMatrixData,
    MacroAnomalyData, VolatilityData, HeatmapData,
    AffordabilityBasketData, SupplyChainMarginData
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
async def get_anomalies(request: Request, date_id: date, commodity_id: int, province_id: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    """
    Early warning list tracking the Top 5 commodities exceeding their 7-day Moving Average window.
    """
    if await check_is_weekend(db, date_id):
        return GenericResponseModel(success=True, data=[])
        
    target_int = date_to_int(date_id)

    join_clause = ""
    where_clause = ""
    params = {"target_date": target_int, "commodity_id": commodity_id}
    
    if province_id is not None:
        join_clause = "JOIN dim_markets m ON f.market_id = m.market_id JOIN dim_regencies r ON m.regency_id = r.regency_id"
        where_clause = "AND r.province_id = :prov_id"
        params["prov_id"] = province_id

    # Using raw SQL with window functions because SQLAlchemy 2.0 window functions with range/rows between 
    # require careful crafting for moving averages over specific date intervals.
    sql = text(f"""
        WITH DailyAvg AS (
            SELECT 
                f.date_id,
                AVG(f.price) as current_price
            FROM fact_daily_prices f
            {join_clause}
            WHERE f.commodity_id = :commodity_id 
              AND f.date_id <= :target_date {where_clause}
            GROUP BY f.date_id
        ),
        MovingAvgs AS (
            SELECT 
                date_id,
                current_price,
                AVG(current_price) OVER (
                    ORDER BY date_id 
                    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
                ) as moving_average_7d
            FROM DailyAvg
        )
        SELECT 
            date_id,
            current_price,
            moving_average_7d,
            ((current_price - moving_average_7d) / NULLIF(moving_average_7d, 0)) * 100 as percentage_difference,
            CASE 
                WHEN current_price >= moving_average_7d THEN 'Spike'
                ELSE 'Drop'
            END as anomaly_type
        FROM MovingAvgs
        WHERE moving_average_7d > 0
          AND ABS(((current_price - moving_average_7d) / NULLIF(moving_average_7d, 0)) * 100) > 0.3
        ORDER BY date_id DESC
        LIMIT 5;
    """)

    result = await db.execute(sql, params)
    rows = result.all()
    
    data = []
    for row in rows:
        data.append({
            "date_id": row.date_id,
            "current_price": row.current_price,
            "moving_average_7d": row.moving_average_7d,
            "percentage_difference": row.percentage_difference,
            "anomaly_type": row.anomaly_type
        })
        
    return GenericResponseModel(success=True, data=data)

@router.get("/macro-anomalies", response_model=GenericResponseModel[List[MacroAnomalyData]])
@cache(expire=43200, key_builder=custom_key_builder)
async def get_macro_anomalies(request: Request, date_id: date, commodity_id: int, province_id: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    """
    Early warning list tracking the Top 5 regencies exceeding their 7-day Moving Average window for a specific commodity on a specific date.
    """
    if await check_is_weekend(db, date_id):
        return GenericResponseModel(success=True, data=[])
        
    target_int = date_to_int(date_id)

    province_where_clause = ""
    params = {"target_date": target_int, "commodity_id": commodity_id}
    
    if province_id is not None:
        province_where_clause = "AND r.province_id = :prov_id"
        params["prov_id"] = province_id

    sql = text(f"""
        WITH TargetDate AS (
            SELECT MAX(date_id) as max_date 
            FROM fact_daily_prices 
            WHERE date_id <= :target_date AND commodity_id = :commodity_id
        ),
        DailyAvg AS (
            SELECT 
                m.regency_id,
                r.regency_name as regency_name,
                f.date_id,
                AVG(f.price) as current_price
            FROM fact_daily_prices f
            JOIN dim_markets m ON f.market_id = m.market_id
            JOIN dim_regencies r ON m.regency_id = r.regency_id
            WHERE f.commodity_id = :commodity_id 
              AND f.date_id <= (SELECT max_date FROM TargetDate)
              {province_where_clause}
            GROUP BY m.regency_id, r.regency_name, f.date_id
        ),
        MovingAvgs AS (
            SELECT 
                regency_id,
                regency_name,
                date_id,
                current_price,
                AVG(current_price) OVER (
                    PARTITION BY regency_id
                    ORDER BY date_id 
                    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
                ) as moving_average_7d
            FROM DailyAvg
        )
        SELECT 
            regency_id,
            regency_name,
            current_price,
            moving_average_7d,
            ((current_price - moving_average_7d) / NULLIF(moving_average_7d, 0)) * 100 as percentage_difference,
            CASE WHEN current_price >= moving_average_7d THEN 'Spike' ELSE 'Drop' END as anomaly_type
        FROM MovingAvgs
        WHERE date_id = (SELECT max_date FROM TargetDate) 
          AND moving_average_7d > 0
        ORDER BY ABS(((current_price - moving_average_7d) / NULLIF(moving_average_7d, 0)) * 100) DESC
        LIMIT 5;
    """)

    result = await db.execute(sql, params)
    rows = result.all()
    
    data = []
    for row in rows:
        data.append({
            "regency_id": row.regency_id,
            "regency_name": row.regency_name,
            "current_price": row.current_price,
            "moving_average_7d": row.moving_average_7d,
            "percentage_difference": row.percentage_difference,
            "anomaly_type": row.anomaly_type
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

@router.get("/volatility", response_model=GenericResponseModel[List[VolatilityData]])
@cache(expire=43200, key_builder=custom_key_builder)
async def get_volatility(request: Request, date_id: date, province_id: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    """
    Calculate the Coefficient of Variation for commodities over the last 30 days.
    """
    target_int = date_to_int(date_id)
    start_int = date_to_int(date_id - timedelta(days=30))

    join_clause = ""
    where_clause = ""
    params = {"target_date": target_int, "start_date": start_int}

    if province_id is not None:
        join_clause = "JOIN dim_markets m ON f.market_id = m.market_id JOIN dim_regencies r ON m.regency_id = r.regency_id"
        where_clause = "AND r.province_id = :prov_id"
        params["prov_id"] = province_id

    sql = text(f"""
        WITH Stats AS (
            SELECT 
                c.commodity_name,
                AVG(f.price) as mean_price,
                STDDEV_POP(f.price) as std_price
            FROM fact_daily_prices f
            JOIN dim_commodities c ON f.commodity_id = c.commodity_id
            {join_clause}
            WHERE f.date_id BETWEEN :start_date AND :target_date {where_clause}
            GROUP BY c.commodity_name
            HAVING COUNT(f.price) > 5
        )
        SELECT 
            commodity_name,
            (std_price / NULLIF(mean_price, 0)) * 100 as cv_percentage
        FROM Stats
        ORDER BY cv_percentage DESC;
    """)

    result = await db.execute(sql, params)
    rows = result.all()
    
    data = [{"commodity_name": r.commodity_name, "cv_percentage": r.cv_percentage or 0} for r in rows]
    return GenericResponseModel(success=True, data=data)

@router.get("/inflation-heatmap", response_model=GenericResponseModel[List[HeatmapData]])
@cache(expire=43200, key_builder=custom_key_builder)
async def get_inflation_heatmap(request: Request, date_id: date, db: AsyncSession = Depends(get_db)):
    """
    Calculate the Month-over-Month percentage difference for each Province & Commodity.
    """
    start_int = date_to_int(date_id - timedelta(days=90))
    target_int = date_to_int(date_id)

    sql = text("""
        WITH MonthlyAvg AS (
            SELECT 
                p.province_name as province_name,
                c.commodity_name,
                DATE_TRUNC('month', TO_DATE(f.date_id::text, 'YYYYMMDD')) as month_date,
                AVG(f.price) as avg_price
            FROM fact_daily_prices f
            JOIN dim_markets m ON f.market_id = m.market_id
            JOIN dim_regencies r ON m.regency_id = r.regency_id
            JOIN dim_provinces p ON r.province_id = p.province_id
            JOIN dim_commodities c ON f.commodity_id = c.commodity_id
            WHERE f.date_id BETWEEN :start_date AND :target_date
            GROUP BY p.province_name, c.commodity_name, month_date
        ),
        MoM_Calc AS (
            SELECT 
                province_name,
                commodity_name,
                month_date,
                avg_price as current_price,
                LAG(avg_price) OVER (PARTITION BY province_name, commodity_name ORDER BY month_date) as prev_price
            FROM MonthlyAvg
        ),
        RankedMoM AS (
            SELECT 
                province_name,
                commodity_name,
                ((current_price - prev_price) / NULLIF(prev_price, 0)) * 100 as mom_percentage,
                ROW_NUMBER() OVER (PARTITION BY province_name, commodity_name ORDER BY month_date DESC) as rn
            FROM MoM_Calc
            WHERE prev_price IS NOT NULL
        )
        SELECT province_name, commodity_name, mom_percentage
        FROM RankedMoM
        WHERE rn = 1;
    """)

    result = await db.execute(sql, {"start_date": start_int, "target_date": target_int})
    rows = result.all()
    
    data = [{
        "province_name": r.province_name,
        "commodity_name": r.commodity_name,
        "mom_percentage": r.mom_percentage or 0
    } for r in rows]
    
    return GenericResponseModel(success=True, data=data)

from fastapi import Query

@router.get("/affordability-basket", response_model=GenericResponseModel[List[AffordabilityBasketData]])
@cache(expire=43200, key_builder=custom_key_builder)
async def get_affordability_basket(
    request: Request, 
    date_id: date, 
    commodity_ids: str = Query(..., description="Comma-separated list of commodity IDs"),
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate the total cost of a predefined group of commodities across different regions (Provinces) on a specific date.
    """
    target_int = date_to_int(date_id)
    
    # Parse commodity_ids
    try:
        comm_ids = [int(cid.strip()) for cid in commodity_ids.split(",") if cid.strip()]
    except ValueError:
        return GenericResponseModel(success=False, data=[], message="Invalid commodity_ids format")
        
    if not comm_ids:
        return GenericResponseModel(success=True, data=[])

    sql = text("""
        WITH RegionalPrices AS (
            SELECT 
                p.province_id,
                p.province_name,
                f.commodity_id,
                AVG(f.price) as avg_price
            FROM fact_daily_prices f
            JOIN dim_markets m ON f.market_id = m.market_id
            JOIN dim_regencies r ON m.regency_id = r.regency_id
            JOIN dim_provinces p ON r.province_id = p.province_id
            WHERE f.date_id = :target_date
              AND f.commodity_id = ANY(:comm_ids)
            GROUP BY p.province_id, p.province_name, f.commodity_id
        )
        SELECT 
            province_name,
            SUM(avg_price) as total_cost
        FROM RegionalPrices
        GROUP BY province_id, province_name
        ORDER BY total_cost DESC;
    """)

    result = await db.execute(sql, {"target_date": target_int, "comm_ids": comm_ids})
    rows = result.all()
    
    data = [{"province_name": r.province_name, "total_cost": r.total_cost} for r in rows]
    return GenericResponseModel(success=True, data=data)

@router.get("/supply-chain-margin", response_model=GenericResponseModel[SupplyChainMarginData])
@cache(expire=43200, key_builder=custom_key_builder)
async def get_supply_chain_margin(
    request: Request, 
    date_id: date, 
    commodity_id: int, 
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate the 30-day average price accumulation and margins across the supply chain nodes:
    Produsen -> Pedagang Besar -> Pasar Tradisional / Pasar Modern.
    """
    target_int = date_to_int(date_id)
    start_int = date_to_int(date_id - timedelta(days=30))

    sql = text("""
        SELECT 
            mt.market_type_name,
            AVG(f.price) as avg_price
        FROM fact_daily_prices f
        JOIN dim_markets m ON f.market_id = m.market_id
        JOIN dim_market_types mt ON m.market_type_id = mt.market_type_id
        WHERE f.date_id BETWEEN :start_date AND :target_date
          AND f.commodity_id = :commodity_id
        GROUP BY mt.market_type_name;
    """)

    result = await db.execute(sql, {"start_date": start_int, "target_date": target_int, "commodity_id": commodity_id})
    rows = result.all()
    
    # Map raw prices to supply chain nodes
    prices = {r.market_type_name: r.avg_price or 0 for r in rows}
    
    produsen_price = prices.get("Produsen", 0)
    wholesale_price = prices.get("Pedagang Besar", 0)
    trad_price = prices.get("Pasar Tradisional", 0)
    modern_price = prices.get("Pasar Modern", 0)
    
    # Fallback missing data conceptually
    if wholesale_price == 0:
        wholesale_price = produsen_price
    if trad_price == 0:
        trad_price = wholesale_price
    if modern_price == 0:
        modern_price = wholesale_price

    data = SupplyChainMarginData(
        producer_price=produsen_price,
        wholesale_price=wholesale_price,
        margin_wholesale=wholesale_price - produsen_price,
        traditional_retail_price=trad_price,
        margin_traditional=trad_price - wholesale_price,
        modern_retail_price=modern_price,
        margin_modern=modern_price - wholesale_price
    )
    
    return GenericResponseModel(success=True, data=data)
