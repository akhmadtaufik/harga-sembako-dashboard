from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models import DimProvince, DimRegency
from app.schemas import DimProvinceSchema, DimRegencySchema, GenericResponseModel

router = APIRouter()

@router.get("/provinces", response_model=GenericResponseModel[List[DimProvinceSchema]])
async def get_provinces(db: AsyncSession = Depends(get_db)):
    """
    Retrieve all provinces.
    """
    result = await db.execute(select(DimProvince).order_by(DimProvince.name))
    provinces = result.scalars().all()
    return GenericResponseModel(success=True, data=list(provinces))

@router.get("/regencies", response_model=GenericResponseModel[List[DimRegencySchema]])
async def get_regencies(province_id: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    """
    Retrieve regencies, optionally filtered by province_id.
    """
    query = select(DimRegency).order_by(DimRegency.name)
    if province_id is not None:
        query = query.filter(DimRegency.province_id == province_id)
        
    result = await db.execute(query)
    regencies = result.scalars().all()
    return GenericResponseModel(success=True, data=list(regencies))
