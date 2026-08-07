from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models import DimProvince, DimRegency
from app.schemas import DimProvinceSchema, DimRegencySchema, GenericResponseModel

router = APIRouter()

@router.get(
    "/provinces", 
    response_model=GenericResponseModel[List[DimProvinceSchema]],
    summary="Get Statically Mapped Provinces",
    response_description="A list of all provinces with their static IDs.",
    tags=["Master Data - Locations"]
)
async def get_provinces(db: AsyncSession = Depends(get_db)):
    """
    Retrieve all provinces.
    
    > **⚠️ CRITICAL:** This is a Master Data endpoint returning strictly static records. The IDs returned here (e.g., `province_id`) **MUST** be utilized as parameters for the `/analytics` endpoints. Clients should not attempt to use string names for queries.
    """
    result = await db.execute(select(DimProvince).order_by(DimProvince.name))
    provinces = result.scalars().all()
    return GenericResponseModel(success=True, data=list(provinces))

@router.get(
    "/regencies", 
    response_model=GenericResponseModel[List[DimRegencySchema]],
    summary="Get Statically Mapped Regencies",
    response_description="A list of all regencies, optionally filtered by parent province.",
    tags=["Master Data - Locations"]
)
async def get_regencies(province_id: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    """
    Retrieve regencies, optionally filtered by `province_id`.
    
    > **⚠️ CRITICAL:** This is a Master Data endpoint returning strictly static records. The IDs returned here (e.g., `regency_id`) **MUST** be utilized as parameters for the `/analytics` endpoints.
    """
    query = select(DimRegency).order_by(DimRegency.name)
    if province_id is not None:
        query = query.filter(DimRegency.province_id == province_id)
        
    result = await db.execute(query)
    regencies = result.scalars().all()
    return GenericResponseModel(success=True, data=list(regencies))
