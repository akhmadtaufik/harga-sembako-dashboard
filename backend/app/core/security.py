from fastapi import Depends
from fastapi.security import APIKeyHeader, HTTPBearer
from app.core.exceptions import UnauthorizedException
from app.core.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
http_bearer = HTTPBearer(auto_error=False)

async def verify_security_credentials(
    api_key: str = Depends(api_key_header),
    token=Depends(http_bearer)
):
    """
    Intercepts requests to verify either a valid API Key or JWT Bearer Token.
    Returns 401 Unauthorized via custom exception if missing or invalid.
    """
    if not api_key and not token:
        raise UnauthorizedException("Missing valid API Key or JWT Bearer token.")
        
    # Basic structural check for the testing phase:
    # Validate API Key if provided
    if api_key and api_key != settings.API_KEY:
        raise UnauthorizedException("Invalid API Key.")
        
    # Validate JWT structure (mock check for phase 3A)
    if token and not getattr(token, "credentials", "").strip():
        raise UnauthorizedException("Invalid JWT Bearer token format.")
        
    return True
