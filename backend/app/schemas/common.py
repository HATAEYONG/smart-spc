"""
Common Schemas
Standard API response wrapper
"""
from pydantic import BaseModel, Generic
from typing import TypeVar, Generic, Optional


T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    """Standard API response wrapper"""
    ok: bool
    data: Optional[T]
    error: Optional[str]
