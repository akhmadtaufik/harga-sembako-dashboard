from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models import DimMarket, DimRegency
from app.schemas import DimMarketSchema, GenericResponseModel

router = APIRouter()

@router.get("", response_model=GenericResponseModel[List[DimMarketSchema]])
async def get_markets(db: AsyncSession = Depends(get_db)):
    """
    Retrieve all markets with geospatial fallback to parent regency coordinates
    if the market's specific coordinates are missing.
    """
    query = (
        select(
            DimMarket.market_id,
            DimMarket.regency_id,
            DimMarket.market_type_id,
            DimMarket.name,
            func.coalesce(DimMarket.latitude, DimRegency.latitude).label("latitude"),
            func.coalesce(DimMarket.longitude, DimRegency.longitude).label("longitude"),
        )
        .join(DimRegency, DimMarket.regency_id == DimRegency.regency_id)
        .order_by(DimMarket.name)
    )
    
    result = await db.execute(query)
    markets = result.all()
    
    # We serialize the row results into Pydantic models directly via the GenericResponseModel
    # Since Row objects map gracefully to dict-like attributes if we map them or Pydantic supports from_attributes
    market_list = []
    for row in markets:
        market_list.append({
            "market_id": row.market_id,
            "regency_id": row.regency_id,
            "market_type_id": row.market_type_id,
            "name": row.name,
            "latitude": row.latitude,
            "longitude": row.longitude,
        })
        
    return GenericResponseModel(success=True, data=market_list)
