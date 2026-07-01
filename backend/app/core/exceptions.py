import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError, DBAPIError
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class GenericErrorResponse(BaseModel):
    success: bool = False
    message: str
    data: list = []

class UnauthorizedException(Exception):
    def __init__(self, message: str = "Unauthorized access details"):
        self.message = message

async def unauthorized_exception_handler(request: Request, exc: UnauthorizedException) -> JSONResponse:
    """
    Handler for missing or invalid authentication credentials.
    """
    logger.warning(f"Unauthorized access on {request.method} {request.url}: {exc.message}")
    return JSONResponse(
        status_code=401,
        content={"success": False, "data": [], "message": exc.message},
    )

async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """
    Catch-all handler for SQLAlchemy errors.
    """
    logger.error(f"SQLAlchemy error on {request.method} {request.url}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "A database error occurred while processing the request."},
    )

async def dbapi_exception_handler(request: Request, exc: DBAPIError) -> JSONResponse:
    """
    Handler for database connectivity drops or engine errors.
    """
    logger.error(f"DBAPI error on {request.method} {request.url}: {str(exc)}")
    return JSONResponse(
        status_code=503,
        content={"success": False, "message": "Database connection is currently unavailable."},
    )

async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Fallback for any unhandled exceptions to prevent stack traces from leaking.
    """
    logger.error(f"Unhandled error on {request.method} {request.url}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "An unexpected internal server error occurred."},
    )
