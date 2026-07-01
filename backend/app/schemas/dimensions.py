from typing import Optional
from pydantic import BaseModel, Field
from datetime import date
from app.schemas.base import ORMBaseModel

class DimDateSchema(ORMBaseModel):
    date_id: date
    year: int
    month: int
    day_name: str
    is_weekend: bool

class DimProvinceSchema(ORMBaseModel):
    province_id: int
    name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class DimRegencySchema(ORMBaseModel):
    regency_id: int
    province_id: int
    name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class DimMarketTypeSchema(ORMBaseModel):
    market_type_id: int
    name: str

class DimMarketSchema(ORMBaseModel):
    market_id: int
    regency_id: int
    market_type_id: int
    name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class DimCommodityGroupSchema(ORMBaseModel):
    group_id: int
    name: str

class DimCommoditySchema(ORMBaseModel):
    commodity_id: int
    group_id: int
    name: str
