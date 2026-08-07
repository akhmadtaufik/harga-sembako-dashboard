from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import date

class SeasonalityData(BaseModel):
    date_id: date = Field(..., description="The specific date of the price record.")
    avg_price: Decimal = Field(..., description="The average price of the commodity on the given date.")
    
    model_config = {
        "json_schema_extra": {
            "examples": [{"date_id": "2023-10-01", "avg_price": "14500.00"}]
        }
    }

class DisparityData(BaseModel):
    regency_id: int = Field(..., description="Static ID of the regency (kota/kabupaten).")
    regency_name: str = Field(..., description="Name of the regency.")
    province_id: int = Field(..., description="Static ID of the province.")
    province_name: str = Field(..., description="Name of the province.")
    latitude: Optional[float] = Field(None, description="Latitude coordinate of the regency.")
    longitude: Optional[float] = Field(None, description="Longitude coordinate of the regency.")
    regency_avg: Decimal = Field(..., description="The average commodity price in this regency.")
    national_avg: Decimal = Field(..., description="The national average price for the commodity on the same date.")
    disparity_percentage: Decimal = Field(..., description="The percentage difference between regency_avg and national_avg.")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "regency_id": 3171, "regency_name": "Kota Jakarta Pusat", 
                "province_id": 31, "province_name": "DKI Jakarta", 
                "latitude": -6.18, "longitude": 106.83, 
                "regency_avg": "15000.00", "national_avg": "14000.00", "disparity_percentage": "7.14"
            }]
        }
    }

class AnomalyData(BaseModel):
    date_id: int = Field(..., description="The date in YYYYMMDD integer format where the anomaly occurred.")
    current_price: Decimal = Field(..., description="The price on the anomaly date.")
    moving_average_7d: Decimal = Field(..., description="The 7-Day Moving Average calculated up to the anomaly date.")
    percentage_difference: Decimal = Field(..., description="Percentage deviation of the current price from the 7D MA.")
    anomaly_type: Optional[str] = Field("Spike", description="Type of anomaly: 'Spike' or 'Drop'.")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "date_id": 20231015, "current_price": "16000.00", 
                "moving_average_7d": "14500.00", "percentage_difference": "10.34", "anomaly_type": "Spike"
            }]
        }
    }

class MarketTypeSpreadData(BaseModel):
    date_id: date = Field(..., description="The specific date of the calculation.")
    market_type_name: str = Field(..., description="The type of market (e.g., 'Pasar Tradisional', 'Pasar Modern').")
    avg_price: Decimal = Field(..., description="The average price for the commodity in this market type.")

    model_config = {
        "json_schema_extra": {
            "examples": [{"date_id": "2023-10-01", "market_type_name": "Pasar Modern", "avg_price": "18000.00"}]
        }
    }

class RegionalMatrixData(BaseModel):
    province_id: int = Field(..., description="Static ID of the province.")
    province_name: str = Field(..., description="Name of the province.")
    average_price: Optional[Decimal] = Field(None, description="Average commodity price in the province.")
    record_count: int = Field(..., description="Number of price records aggregated.")

    model_config = {
        "json_schema_extra": {
            "examples": [{"province_id": 31, "province_name": "DKI Jakarta", "average_price": "14500.00", "record_count": 120}]
        }
    }

class MacroAnomalyData(BaseModel):
    regency_id: int = Field(..., description="Static ID of the regency.")
    regency_name: str = Field(..., description="Name of the regency.")
    current_price: Decimal = Field(..., description="The average price on the latest date.")
    moving_average_7d: Decimal = Field(..., description="The 7-Day Moving Average for the regency.")
    percentage_difference: Decimal = Field(..., description="Percentage deviation from the 7D MA.")
    anomaly_type: Optional[str] = Field("Spike", description="'Spike' or 'Drop' based on the percentage deviation.")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "regency_id": 3171, "regency_name": "Kota Jakarta Pusat", "current_price": "16500.00", 
                "moving_average_7d": "14000.00", "percentage_difference": "17.85", "anomaly_type": "Spike"
            }]
        }
    }

class VolatilityData(BaseModel):
    commodity_name: str = Field(..., description="Name of the commodity analyzed.")
    cv_percentage: Decimal = Field(..., description="Coefficient of Variation (CV) percentage representing volatility (StdDev / Mean * 100).")

    model_config = {
        "json_schema_extra": {
            "examples": [{"commodity_name": "Beras Medium", "cv_percentage": "5.43"}]
        }
    }

class HeatmapData(BaseModel):
    province_name: str = Field(..., description="Name of the province.")
    commodity_name: str = Field(..., description="Name of the commodity.")
    mom_percentage: Decimal = Field(..., description="Month-over-Month (MoM) percentage difference in average price.")

    model_config = {
        "json_schema_extra": {
            "examples": [{"province_name": "DKI Jakarta", "commodity_name": "Beras Premium", "mom_percentage": "2.1"}]
        }
    }

class AffordabilityBasketData(BaseModel):
    province_name: str = Field(..., description="Name of the province.")
    total_cost: Decimal = Field(..., description="The sum of average prices of the selected commodities in the basket.")

    model_config = {
        "json_schema_extra": {
            "examples": [{"province_name": "Jawa Barat", "total_cost": "65000.00"}]
        }
    }

class SupplyChainMarginData(BaseModel):
    producer_price: Decimal = Field(..., description="Average price at the Producer (Produsen) level.")
    wholesale_price: Decimal = Field(..., description="Average price at the Wholesale (Pedagang Besar) level.")
    margin_wholesale: Decimal = Field(..., description="Absolute margin between Wholesale and Producer prices.")
    traditional_retail_price: Decimal = Field(..., description="Average price at Traditional Markets.")
    margin_traditional: Decimal = Field(..., description="Absolute margin between Traditional Retail and Wholesale prices.")
    modern_retail_price: Decimal = Field(..., description="Average price at Modern Retail Markets.")
    margin_modern: Decimal = Field(..., description="Absolute margin between Modern Retail and Wholesale prices.")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "producer_price": "10000.00", "wholesale_price": "11000.00", "margin_wholesale": "1000.00",
                "traditional_retail_price": "12500.00", "margin_traditional": "1500.00",
                "modern_retail_price": "15000.00", "margin_modern": "4000.00"
            }]
        }
    }

class PredictiveTrajectoryData(BaseModel):
    date_id: date = Field(..., description="The date of the actual or forecasted price.")
    actual_price: Optional[Decimal] = Field(None, description="The actual recorded average price, if in the past.")
    forecast_price: Optional[Decimal] = Field(None, description="The forecasted price generated via Linear Regression, if in the future.")
    upper_bound: Optional[Decimal] = Field(None, description="Upper confidence interval bound for the forecast.")
    lower_bound: Optional[Decimal] = Field(None, description="Lower confidence interval bound for the forecast.")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "date_id": "2023-11-01", "actual_price": None, "forecast_price": "14200.00",
                "upper_bound": "14500.00", "lower_bound": "13900.00"
            }]
        }
    }

class CrossCorrelationData(BaseModel):
    commodity_name: str = Field(..., description="Name of the correlated substitute/complementary commodity.")
    correlation_score: Decimal = Field(..., description="Pearson correlation coefficient (-1.0 to 1.0) indicating relationship strength.")

    model_config = {
        "json_schema_extra": {
            "examples": [{"commodity_name": "Telur Ayam Ras", "correlation_score": "0.85"}]
        }
    }

class MarketClusterData(BaseModel):
    market_id: int = Field(..., description="Static ID of the local market.")
    market_name: str = Field(..., description="Name of the market.")
    average_price: Decimal = Field(..., description="The 30-day average price for the commodity in this market.")
    volatility: Decimal = Field(..., description="The standard deviation (volatility) of the price over the last 30 days.")
    anomaly_count: int = Field(..., description="The frequency of recorded anomalies (Spikes/Drops) in this market.")
    cluster_label: str = Field(..., description="Assigned cluster category (e.g., 'High Price, High Volatility', 'Stable Baseline').")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "market_id": 1, "market_name": "Pasar Induk Kramat Jati", "average_price": "14000.00",
                "volatility": "500.25", "anomaly_count": 3, "cluster_label": "High Volatility"
            }]
        }
    }
