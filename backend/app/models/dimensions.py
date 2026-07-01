from sqlalchemy import Column, Integer, String, Float, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class DimDate(Base):
    __tablename__ = "dim_dates"

    date_id = Column(Integer, primary_key=True, index=True)
    full_date = Column(Date, nullable=False, unique=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    day_name = Column(String(20), nullable=False)
    is_weekend = Column(Boolean, nullable=False, default=False)

class DimProvince(Base):
    __tablename__ = "dim_provinces"

    province_id = Column(Integer, primary_key=True, index=True)
    name = Column("province_name", String(100), nullable=False, unique=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    regencies = relationship("DimRegency", back_populates="province")

class DimRegency(Base):
    __tablename__ = "dim_regencies"

    regency_id = Column(Integer, primary_key=True, index=True)
    province_id = Column(Integer, ForeignKey("dim_provinces.province_id"), nullable=False)
    name = Column("regency_name", String(100), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    province = relationship("DimProvince", back_populates="regencies")
    markets = relationship("DimMarket", back_populates="regency")

class DimMarketType(Base):
    __tablename__ = "dim_market_types"

    market_type_id = Column(Integer, primary_key=True, index=True)
    name = Column("market_type_name", String(50), nullable=False, unique=True)

    markets = relationship("DimMarket", back_populates="market_type")

class DimMarket(Base):
    __tablename__ = "dim_markets"

    market_id = Column(Integer, primary_key=True, index=True)
    regency_id = Column(Integer, ForeignKey("dim_regencies.regency_id"), nullable=False)
    market_type_id = Column(Integer, ForeignKey("dim_market_types.market_type_id"), nullable=False)
    name = Column("market_name", String(150), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    regency = relationship("DimRegency", back_populates="markets")
    market_type = relationship("DimMarketType", back_populates="markets")

class DimCommodityGroup(Base):
    __tablename__ = "dim_commodity_groups"

    group_id = Column(Integer, primary_key=True, index=True)
    name = Column("group_name", String(100), nullable=False, unique=True)

    commodities = relationship("DimCommodity", back_populates="group")

class DimCommodity(Base):
    __tablename__ = "dim_commodities"

    commodity_id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("dim_commodity_groups.group_id"), nullable=False)
    name = Column("commodity_name", String(150), nullable=False, unique=True)

    group = relationship("DimCommodityGroup", back_populates="commodities")
