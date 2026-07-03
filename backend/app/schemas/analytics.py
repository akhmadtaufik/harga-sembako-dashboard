from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import date

class SeasonalityData(BaseModel):
    date_id: date
    avg_price: Decimal

class DisparityData(BaseModel):
    regency_id: int
    regency_name: str
    province_id: int
    province_name: str
    latitude: Optional[float]
    longitude: Optional[float]
    regency_avg: Decimal
    national_avg: Decimal
    disparity_percentage: Decimal

class AnomalyData(BaseModel):
    commodity_id: int
    commodity_name: str
    current_price: Decimal
    moving_average_7d: Decimal
    percentage_difference: Decimal

class MarketTypeSpreadData(BaseModel):
    date_id: date
    market_type_name: str
    avg_price: Decimal

class RegionalMatrixData(BaseModel):
    province_id: int
    province_name: str
    average_price: Optional[Decimal]
    record_count: int
