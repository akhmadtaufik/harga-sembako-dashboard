from sqlalchemy import Column, Integer, Numeric, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class FactDailyPrice(Base):
    __tablename__ = "fact_daily_prices"

    date_id = Column(Date, ForeignKey("dim_dates.date_id"), primary_key=True)
    market_id = Column(Integer, ForeignKey("dim_markets.market_id"), primary_key=True)
    commodity_id = Column(Integer, ForeignKey("dim_commodities.commodity_id"), primary_key=True)
    
    # Store price as numeric/decimal to avoid floating point inaccuracies
    price = Column(Numeric(15, 2), nullable=False)

    # Relationships to dimensions
    date = relationship("DimDate")
    market = relationship("DimMarket")
    commodity = relationship("DimCommodity")
