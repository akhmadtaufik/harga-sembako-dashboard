from pydantic import BaseModel
from datetime import date
from decimal import Decimal
from app.schemas.base import ORMBaseModel

class FactDailyPriceSchema(ORMBaseModel):
    date_id: date
    market_id: int
    commodity_id: int
    price: Decimal
