from typing import Optional
from pydantic import BaseModel, Field
from datetime import date
from app.schemas.base import ORMBaseModel

class DimDateSchema(ORMBaseModel):
    date_id: date = Field(..., description="The date record.")
    year: int = Field(..., description="Year component.")
    month: int = Field(..., description="Month component (1-12).")
    day_name: str = Field(..., description="Name of the day.")
    is_weekend: bool = Field(..., description="Boolean flag indicating if the date falls on a weekend.")

class DimProvinceSchema(ORMBaseModel):
    province_id: int = Field(..., description="Static national administrative code for the province. Must be used as a parameter for Analytics endpoints.")
    name: str = Field(..., description="Name of the province.")
    latitude: Optional[float] = Field(None, description="Latitude coordinate of the province center.")
    longitude: Optional[float] = Field(None, description="Longitude coordinate of the province center.")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "province_id": 31,
                "name": "DKI Jakarta",
                "latitude": -6.1751,
                "longitude": 106.8272
            }]
        }
    }

class DimRegencySchema(ORMBaseModel):
    regency_id: int = Field(..., description="Static national administrative code for the regency (Kota/Kabupaten). Mandatory for Micro Deep-Dive Analytics.")
    province_id: int = Field(..., description="Static ID of the parent province.")
    name: str = Field(..., description="Name of the regency.")
    latitude: Optional[float] = Field(None, description="Latitude coordinate of the regency.")
    longitude: Optional[float] = Field(None, description="Longitude coordinate of the regency.")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "regency_id": 3171,
                "province_id": 31,
                "name": "Kota Jakarta Pusat",
                "latitude": -6.18,
                "longitude": 106.83
            }]
        }
    }

class DimMarketTypeSchema(ORMBaseModel):
    market_type_id: int = Field(..., description="Static ID for the market classification.")
    name: str = Field(..., description="Type of the market (e.g., 'Pasar Tradisional' [Baseline], 'Pasar Modern' [Variant]).")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "market_type_id": 1,
                "name": "Pasar Tradisional"
            }]
        }
    }

class DimMarketSchema(ORMBaseModel):
    market_id: int = Field(..., description="Static ID for the individual market. Maps directly to specific geographical retail points.")
    regency_id: int = Field(..., description="Static ID of the parent regency.")
    market_type_id: int = Field(..., description="Static ID classifying if this is a Baseline (Traditional) or Variant (Modern/Wholesale) market.")
    name: str = Field(..., description="Name of the market.")
    latitude: Optional[float] = Field(None, description="Precise latitude coordinate of the market.")
    longitude: Optional[float] = Field(None, description="Precise longitude coordinate of the market.")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "market_id": 101,
                "regency_id": 3171,
                "market_type_id": 1,
                "name": "Pasar Senen",
                "latitude": -6.1764,
                "longitude": 106.8423
            }]
        }
    }

class DimCommodityGroupSchema(ORMBaseModel):
    group_id: int = Field(..., description="Static ID for the commodity category.")
    name: str = Field(..., description="Name of the commodity category (e.g., 'Beras', 'Daging').")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "group_id": 1,
                "name": "Beras"
            }]
        }
    }

class DimCommoditySchema(ORMBaseModel):
    commodity_id: int = Field(..., description="Static ID for the granular commodity item. Mandatory for all Analytics endpoints.")
    group_id: int = Field(..., description="Static ID of the parent commodity group.")
    name: str = Field(..., description="Name of the commodity. Note: Prices in analytics are always normalized per Kg or per Liter depending on the nature of this item.")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "commodity_id": 1,
                "group_id": 1,
                "name": "Beras Medium"
            }]
        }
    }
