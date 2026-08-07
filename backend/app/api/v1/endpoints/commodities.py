from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models import DimCommodityGroup, DimCommodity
from app.schemas import DimCommodityGroupSchema, DimCommoditySchema, GenericResponseModel

router = APIRouter()

@router.get(
    "/groups", 
    response_model=GenericResponseModel[List[DimCommodityGroupSchema]],
    summary="Get Statically Mapped Commodity Groups",
    response_description="A list of high-level commodity categories.",
    tags=["Master Data - Commodities"]
)
async def get_commodity_groups(db: AsyncSession = Depends(get_db)):
    """
    Retrieve all commodity groups.
    
    > **⚠️ CRITICAL:** This is a Master Data endpoint returning strictly static records. The IDs returned here **MUST** be utilized as parameters for the `/analytics` endpoints.
    """
    result = await db.execute(select(DimCommodityGroup).order_by(DimCommodityGroup.name))
    groups = result.scalars().all()
    return GenericResponseModel(success=True, data=list(groups))

@router.get(
    "/items", 
    response_model=GenericResponseModel[List[DimCommoditySchema]],
    summary="Get Statically Mapped Commodities",
    response_description="A list of granular commodity items.",
    tags=["Master Data - Commodities"]
)
async def get_commodities(db: AsyncSession = Depends(get_db)):
    """
    Retrieve all commodities at the granular item level.
    
    > **⚠️ CRITICAL:** This is a Master Data endpoint returning strictly static records. The `commodity_id` returned here **MUST** be utilized as a parameter for all analytics endpoints. Note that analytics formulas always normalize prices per Kg or per Liter based on these items.
    """
    result = await db.execute(select(DimCommodity).order_by(DimCommodity.name))
    items = result.scalars().all()
    return GenericResponseModel(success=True, data=list(items))
