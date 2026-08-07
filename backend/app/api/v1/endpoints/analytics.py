from typing import List, Optional
from datetime import date, timedelta, datetime
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
    AffordabilityBasketData, SupplyChainMarginData,
    PredictiveTrajectoryData, CrossCorrelationData, MarketClusterData
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

@router.get(
    "/seasonality", 
    response_model=GenericResponseModel[List[SeasonalityData]],
    summary="Get Seasonality Time-Series",
    response_description="A list of daily average prices for the specified commodity and year.",
    tags=["Macro Analytics"]
)
@cache(expire=43200, key_builder=custom_key_builder)
async def get_seasonality(request: Request, commodity_id: int, year: int, db: AsyncSession = Depends(get_db)):
    """
    Aggregate prices by day for time-series trends based on a specific commodity.
    
    ### Analytics Methodology
    Calculates the national average price per day for a specific year to expose cyclical patterns and seasonal harvesting effects.
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

@router.get(
    "/disparity", 
    response_model=GenericResponseModel[List[DisparityData]],
    summary="Get Regional Price Disparity",
    response_description="A list of regencies with their average price and disparity against the national baseline.",
    tags=["Macro Analytics"]
)
@cache(expire=43200, key_builder=custom_key_builder)
async def get_disparity(request: Request, date_id: date, commodity_id: int, province_id: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    """
    Compare regional averages against the national baseline for the Choropleth map layer.
    
    ### Analytics Methodology
    Computes the percentage difference between a specific regency\'s daily average price and the national average price. Disparity > 0 indicates premium pricing.
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

@router.get(
    "/anomalies", 
    response_model=GenericResponseModel[List[AnomalyData]],
    summary="Get Commodity Historical Anomalies",
    response_description="A list of the top 5 historical anomalies (spikes or drops) for a commodity.",
    tags=["Macro Analytics"]
)
@cache(expire=43200, key_builder=custom_key_builder)
async def get_anomalies(request: Request, date_id: date, commodity_id: int, province_id: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    """
    Early warning list tracking historical price anomalies.
    
    ### Analytics Methodology
    Uses a 7-Day Moving Average (7D MA) baseline. An anomaly is flagged if the current daily price deviates from the 7D MA by more than a predefined threshold. Classifies deviations as `Spike` or `Drop`.
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

@router.get(
    "/macro-anomalies", 
    response_model=GenericResponseModel[List[MacroAnomalyData]],
    summary="Get Regional Macro Anomalies",
    response_description="A list of the top 5 regencies experiencing the highest price deviations today.",
    tags=["Macro Analytics"]
)
@cache(expire=43200, key_builder=custom_key_builder)
async def get_macro_anomalies(request: Request, date_id: date, commodity_id: int, province_id: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    """
    Early warning list tracking the Top 5 regencies exceeding their 7-day Moving Average window for a specific commodity on a specific date.
    
    ### Analytics Methodology
    Aggregates prices per regency and calculates the 7-Day Moving Average. Sorts regencies by the absolute percentage difference to highlight areas with extreme supply chain shocks.
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

@router.get(
    "/spread/market-types", 
    response_model=GenericResponseModel[List[MarketTypeSpreadData]],
    summary="Get Market Type Spread Analysis",
    response_description="A time-series list comparing average prices across different market types.",
    tags=["Micro Deep-Dive Analytics"]
)
@cache(expire=43200, key_builder=custom_key_builder)
async def get_market_type_spread(request: Request, start_date: date, end_date: date, commodity_id: int, regency_id: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    """
    Calculate structural pricing spreads between Traditional, Modern, Wholesaler, and Producer classifications for a specific commodity.
    
    ### Analytics Methodology
    Groups daily prices by Market Type. The UI calculates the margin premium using the formula: `((Modern - Traditional) / Traditional) * 100`. A widening margin indicates high retail premiums or supply disparities.
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
    
    if regency_id is not None:
        query = query.where(DimMarket.regency_id == regency_id)
        
    query = query.group_by(DimDate.full_date, DimMarketType.name).order_by(DimDate.full_date, DimMarketType.name)
    
    result = await db.execute(query)
    rows = result.all()
    
    if not rows:
        return GenericResponseModel(success=True, data=[])
        
    data = [{"date_id": row.date_id, "market_type_name": row.market_type_name, "avg_price": row.avg_price} for row in rows]
    return GenericResponseModel(success=True, data=data)

@router.get(
    "/regional-matrix", 
    response_model=GenericResponseModel[List[RegionalMatrixData]],
    summary="Get Regional Averages Matrix",
    response_description="A list of provincial average prices and data point counts.",
    tags=["Macro Analytics"]
)
@cache(expire=43200, key_builder=custom_key_builder)
async def get_regional_matrix(request: Request, date_id: date, commodity_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get aggregated regional averages matrix data.
    
    ### Analytics Methodology
    Rolls up market-level price data to the Provincial level, returning both the average price and the count of records to assess data density and reliability.
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

@router.get(
    "/volatility", 
    response_model=GenericResponseModel[List[VolatilityData]],
    summary="Get Commodity Volatility Index",
    response_description="A ranked list of commodities by their 30-day volatility index.",
    tags=["Macro Analytics"]
)
@cache(expire=43200, key_builder=custom_key_builder)
async def get_volatility(request: Request, date_id: date, province_id: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    """
    Calculate the Coefficient of Variation for commodities over the last 30 days.
    
    ### Analytics Methodology
    Uses the Coefficient of Variation (CV) formula: `(Standard Deviation / Mean) * 100`. This normalizes volatility across commodities with drastically different base prices (e.g., Beef vs. Rice), allowing for an apples-to-apples risk comparison.
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

@router.get(
    "/inflation-heatmap", 
    response_model=GenericResponseModel[List[HeatmapData]],
    summary="Get Month-over-Month Inflation Heatmap",
    response_description="A matrix of MoM price changes for commodities across provinces.",
    tags=["Macro Analytics"]
)
@cache(expire=43200, key_builder=custom_key_builder)
async def get_inflation_heatmap(request: Request, date_id: date, db: AsyncSession = Depends(get_db)):
    """
    Calculate the Month-over-Month percentage difference for each Province & Commodity.
    
    ### Analytics Methodology
    Truncates dates to the month level, averages the prices, and uses SQL Window Functions (`LAG`) to compute the percentage difference between the current month and the previous month.
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

@router.get(
    "/affordability-basket", 
    response_model=GenericResponseModel[List[AffordabilityBasketData]],
    summary="Get Regional Affordability Basket",
    response_description="The total cost of a custom basket of goods per province.",
    tags=["Macro Analytics"]
)
@cache(expire=43200, key_builder=custom_key_builder)
async def get_affordability_basket(
    request: Request, 
    date_id: date, 
    commodity_ids: str = Query(..., description="Comma-separated list of commodity IDs"),
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate the total cost of a predefined group of commodities across different regions (Provinces) on a specific date.
    
    ### Analytics Methodology
    Sums the average prices of a dynamic list of commodities for each province. Used to measure the purchasing power parity and basic living costs across regions.
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

@router.get(
    "/supply-chain-margin", 
    response_model=GenericResponseModel[SupplyChainMarginData],
    summary="Get Supply Chain Margin Analysis",
    response_description="Average prices and margins across the 4 major supply chain nodes.",
    tags=["Micro Deep-Dive Analytics"]
)
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
    
    ### Analytics Methodology
    Averages the last 30 days of data grouped by Market Type. Calculates the absolute margin added at each step of the supply chain to identify bottlenecks or price gouging.
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
@router.get(
    "/predictive-trajectory", 
    response_model=GenericResponseModel[List[PredictiveTrajectoryData]],
    summary="Get Predictive Price Trajectory (14D)",
    response_description="A list containing 90 days of historical actuals and 14 days of linear regression forecasts.",
    tags=["Micro Deep-Dive Analytics"]
)
@cache(expire=43200, key_builder=custom_key_builder)
async def get_predictive_trajectory(
    commodity_id: int,
    regency_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Forecast the next 14 days of prices for a commodity in a specific regency.
    
    ### Analytics Methodology
    Extracts the last 90 days of prices, interpolates missing dates, and applies a degree-1 Polynomial Fit (Linear Regression) via Numpy to project the next 14 days. An expanding confidence interval (2% to 5%) is applied to denote increasing uncertainty over time.
    """
    import pandas as pd
    import numpy as np
    
    # 1. Fetch 90 days of history
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=90)
    
    end_date_int = date_to_int(end_date)
    start_date_int = date_to_int(start_date)
    
    query = (
        select(
            FactDailyPrice.date_id,
            func.avg(FactDailyPrice.price).label("avg_price")
        )
        .join(DimMarket, FactDailyPrice.market_id == DimMarket.market_id)
        .where(
            FactDailyPrice.commodity_id == commodity_id,
            DimMarket.regency_id == regency_id,
            FactDailyPrice.date_id >= start_date_int,
            FactDailyPrice.date_id <= end_date_int,
            FactDailyPrice.price > 0
        )
        .group_by(FactDailyPrice.date_id)
        .order_by(FactDailyPrice.date_id)
    )
    
    result = await db.execute(query)
    rows = result.fetchall()
    
    if not rows:
        return GenericResponseModel(success=True, data=[])
        
    df = pd.DataFrame([{"date_id": str(r.date_id), "price": float(r.avg_price)} for r in rows])
    df["date_id"] = pd.to_datetime(df["date_id"], format="%Y%m%d")
    df = df.set_index("date_id").asfreq("D")
    df["price"] = df["price"].interpolate(method="linear")
    
    # Calculate Linear Regression (numpy.polyfit)
    x = np.arange(len(df))
    y = df["price"].values
    
    if len(df) < 2:
        return GenericResponseModel(success=True, data=[])
        
    coefficients = np.polyfit(x, y, 1)
    poly_func = np.poly1d(coefficients)
    
    # Forecast 14 days
    last_date = df.index[-1]
    forecast_dates = [last_date + timedelta(days=i) for i in range(1, 15)]
    x_forecast = np.arange(len(df), len(df) + 14)
    y_forecast = poly_func(x_forecast)
    
    output = []
    
    # Append Actuals
    for i, (idx, row) in enumerate(df.iterrows()):
        output.append(
            PredictiveTrajectoryData(
                date_id=idx.date(),
                actual_price=Decimal(str(round(row["price"])))
            )
        )
        
    # Append Forecasts with confidence bounds
    for i, (f_date, f_price) in enumerate(zip(forecast_dates, y_forecast)):
        # Expand confidence bound linearly from 2% to 5% over 14 days
        conf_pct = 0.02 + (i / 13) * 0.03
        upper = f_price * (1 + conf_pct)
        lower = f_price * (1 - conf_pct)
        
        output.append(
            PredictiveTrajectoryData(
                date_id=f_date.date(),
                forecast_price=Decimal(str(round(f_price))),
                upper_bound=Decimal(str(round(upper))),
                lower_bound=Decimal(str(round(lower)))
            )
        )
        
    return GenericResponseModel(success=True, data=output)


@router.get(
    "/correlation", 
    response_model=GenericResponseModel[List[CrossCorrelationData]],
    summary="Get Cross-Commodity Correlation",
    response_description="The top 5 most correlated commodities based on 90-day historical prices.",
    tags=["Micro Deep-Dive Analytics"]
)
@cache(expire=43200, key_builder=custom_key_builder)
async def get_cross_correlation(
    commodity_id: int,
    regency_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Identify substitute or complementary commodities using Pearson correlation.
    
    ### Analytics Methodology
    Pivots 90 days of price data for all commodities in a regency into a time-series matrix. Interpolates missing values, then calculates the Pearson correlation coefficient matrix. Returns the top 5 commodities with the highest absolute correlation to the target commodity.
    """
    import pandas as pd
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=90)
    
    end_date_int = date_to_int(end_date)
    start_date_int = date_to_int(start_date)
    
    query = (
        select(
            FactDailyPrice.date_id,
            DimCommodity.name.label("commodity_name"),
            DimCommodity.commodity_id,
            func.avg(FactDailyPrice.price).label("avg_price")
        )
        .join(DimMarket, FactDailyPrice.market_id == DimMarket.market_id)
        .join(DimCommodity, FactDailyPrice.commodity_id == DimCommodity.commodity_id)
        .where(
            DimMarket.regency_id == regency_id,
            FactDailyPrice.date_id >= start_date_int,
            FactDailyPrice.date_id <= end_date_int,
            FactDailyPrice.price > 0
        )
        .group_by(FactDailyPrice.date_id, DimCommodity.commodity_id, DimCommodity.name)
    )
    
    result = await db.execute(query)
    rows = result.fetchall()
    
    if not rows:
        return GenericResponseModel(success=True, data=[])
        
    # Build DataFrame
    df = pd.DataFrame([{
        "date_id": r.date_id,
        "commodity_id": r.commodity_id,
        "commodity_name": r.commodity_name,
        "price": float(r.avg_price)
    } for r in rows])
    
    # Check if target commodity exists in the regency
    target_name = df[df["commodity_id"] == commodity_id]["commodity_name"].unique()
    if len(target_name) == 0:
        return GenericResponseModel(success=True, data=[])
    target_name = target_name[0]
    
    # Pivot to get dates as rows and commodities as columns
    pivot_df = df.pivot_table(index="date_id", columns="commodity_name", values="price")
    
    # Drop commodities with too much missing data
    min_periods = int(len(pivot_df) * 0.5)
    pivot_df = pivot_df.dropna(axis=1, thresh=min_periods)
    
    if target_name not in pivot_df.columns:
        return GenericResponseModel(success=True, data=[])
        
    # Interpolate remaining missing values linearly
    pivot_df = pivot_df.interpolate(method="linear").fillna(method="bfill").fillna(method="ffill")
    
    # Calculate Pearson Correlation
    corr_matrix = pivot_df.corr(method="pearson")
    target_corr = corr_matrix[target_name].drop(target_name, errors="ignore")
    
    # Filter top 5 absolute correlations to surface substitutes/complements
    top_corr = target_corr.abs().sort_values(ascending=False).head(5)
    
    output = []
    for comm_name in top_corr.index:
        score = target_corr[comm_name]
        if not pd.isna(score):
            output.append(
                CrossCorrelationData(
                    commodity_name=comm_name,
                    correlation_score=Decimal(str(round(score, 4)))
                )
            )
            
    return GenericResponseModel(success=True, data=output)

@router.get(
    "/market-clusters", 
    response_model=GenericResponseModel[List[MarketClusterData]],
    summary="Get Market Behavior Clusters (30D)",
    response_description="A list of markets categorized into clusters based on price and volatility.",
    tags=["Micro Deep-Dive Analytics"]
)
@cache(expire=43200, key_builder=custom_key_builder)
async def get_market_clusters(
    commodity_id: int,
    regency_id: int,
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """
    Segment markets into behavioral clusters based on Price and Volatility.
    
    ### Analytics Methodology
    Aggregates 30 days of market prices to compute Mean (X-axis) and Standard Deviation (Y-axis). Applies Scikit-Learn\'s K-Means clustering (k=3) if there are 5 or more markets. Falls back to Statistical Binning (Percentiles) if the sample size is too small for K-Means.
    """
    import pandas as pd
    import numpy as np
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    end_date_int = date_to_int(end_date)
    start_date_int = date_to_int(start_date)

    query = (
        select(
            FactDailyPrice.date_id,
            FactDailyPrice.market_id,
            DimMarket.name.label("market_name"),
            FactDailyPrice.price
        )
        .join(DimMarket, FactDailyPrice.market_id == DimMarket.market_id)
        .where(
            FactDailyPrice.commodity_id == commodity_id,
            DimMarket.regency_id == regency_id,
            FactDailyPrice.date_id >= start_date_int,
            FactDailyPrice.date_id <= end_date_int,
            FactDailyPrice.price > 0
        )
    )
    
    result = await db.execute(query)
    rows = result.fetchall()
    
    if not rows:
        return GenericResponseModel(success=True, data=[])
        
    df = pd.DataFrame([{
        "date_id": r.date_id,
        "market_id": r.market_id,
        "market_name": r.market_name,
        "price": float(r.price)
    } for r in rows])
    
    # Calculate per-market metrics
    market_stats = []
    
    for market_id, group in df.groupby("market_id"):
        mean_price = group["price"].mean()
        std_price = group["price"].std()
        if pd.isna(std_price):
            std_price = 0
            
        # Count anomalies: days where price > mean + 2*std or price < mean - 2*std
        if std_price > 0:
            anomalies = group[(group["price"] > mean_price + 2*std_price) | (group["price"] < mean_price - 2*std_price)]
            anomaly_count = len(anomalies)
        else:
            anomaly_count = 0
            
        market_stats.append({
            "market_id": market_id,
            "market_name": group["market_name"].iloc[0],
            "average_price": mean_price,
            "volatility": std_price,
            "anomaly_count": anomaly_count
        })
        
    stats_df = pd.DataFrame(market_stats)
    
    if len(stats_df) < 5:
        # Sample size N < 5: Use simple mean comparisons
        overall_mean = stats_df["average_price"].mean()
        
        data = []
        for _, row in stats_df.iterrows():
            if row.average_price > overall_mean:
                label = "Premium"
            else:
                label = "Baseline"
                
            data.append(
                MarketClusterData(
                    market_id=row.market_id,
                    market_name=row.market_name,
                    average_price=Decimal(str(round(row.average_price))),
                    volatility=Decimal(str(round(row.volatility))),
                    anomaly_count=row.anomaly_count,
                    cluster_label=label
                )
            )
        return GenericResponseModel(success=True, data=data)

    # Sample size N >= 5: Use K-Means Clustering
    X = stats_df[["average_price", "volatility"]].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    k = min(3, len(stats_df) // 2)
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X_scaled)
    
    stats_df["cluster"] = clusters
    
    # Sort centroids by average price to assign logical names
    cluster_means = stats_df.groupby("cluster")["average_price"].mean().sort_values()
    
    # Map cluster index to labels
    labels_map = {}
    if k == 3:
        logical_names = ["Budget", "Baseline", "Premium"]
    else:
        logical_names = ["Baseline", "Premium"]
        
    for i, cluster_idx in enumerate(cluster_means.index):
        labels_map[cluster_idx] = logical_names[i]
        
    output = []
    for _, row in stats_df.iterrows():
        cluster_id = int(row["cluster"])
        label = labels_map[cluster_id]
        
        output.append(
            MarketClusterData(
                market_id=row["market_id"],
                market_name=row["market_name"],
                average_price=Decimal(str(round(row["average_price"]))),
                volatility=Decimal(str(round(row["volatility"]))),
                anomaly_count=int(row["anomaly_count"]),
                cluster_label=label
            )
        )
        
    return GenericResponseModel(success=True, data=output)
