from fastapi import APIRouter, Depends

from app.api.v1.endpoints import locations, commodities, markets, analytics
from app.core.security import verify_security_credentials

router = APIRouter()

router.include_router(locations.router, prefix="/locations", tags=["locations"], dependencies=[Depends(verify_security_credentials)])
router.include_router(commodities.router, prefix="/commodities", tags=["commodities"], dependencies=[Depends(verify_security_credentials)])
router.include_router(markets.router, prefix="/markets", tags=["markets"], dependencies=[Depends(verify_security_credentials)])
router.include_router(analytics.router, prefix="/analytics", tags=["analytics"], dependencies=[Depends(verify_security_credentials)])
