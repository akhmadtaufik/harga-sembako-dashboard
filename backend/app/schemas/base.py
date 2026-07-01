from typing import Generic, TypeVar, Optional, List, Any
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")

class GenericResponseModel(BaseModel, Generic[T]):
    """
    Standard generic response envelope.
    All API responses should inherit or use this model.
    """
    success: bool = True
    data: Optional[T] = None
    message: Optional[str] = None

class ORMBaseModel(BaseModel):
    """
    Base configuration for Pydantic models mapping to ORM objects.
    """
    model_config = ConfigDict(from_attributes=True)
