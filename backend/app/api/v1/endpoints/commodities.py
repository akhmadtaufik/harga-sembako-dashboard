from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models import DimCommodityGroup, DimCommodity
from app.schemas import DimCommodityGroupSchema, DimCommoditySchema, GenericResponseModel

router = APIRouter()

@router.get("/groups", response_model=GenericResponseModel[List[DimCommodityGroupSchema]])
async def get_commodity_groups(db: AsyncSession = Depends(get_db)):
    """
    Retrieve all commodity groups.
    """
    result = await db.execute(select(DimCommodityGroup).order_by(DimCommodityGroup.name))
    groups = result.scalars().all()
    return GenericResponseModel(success=True, data=list(groups))

@router.get("/items", response_model=GenericResponseModel[List[DimCommoditySchema]])
async def get_commodities(db: AsyncSession = Depends(get_db)):
    """
    Retrieve all commodities at the granular item level.
    """
    result = await db.execute(select(DimCommodity).order_by(DimCommodity.name))
    items = result.scalars().all()
    return GenericResponseModel(success=True, data=list(items))
