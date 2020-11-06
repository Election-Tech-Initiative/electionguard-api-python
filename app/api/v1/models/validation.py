from typing import Any, Optional
from .base import Base

__all__ = ["BaseValidationRequest", "ValidationResponse", "Schema"]

Schema = Any


class BaseValidationRequest(Base):
    """Base validation request"""

    schema_override: Optional[Schema] = None


class ValidationResponse(Base):
    """Response for validating models"""

    success: bool
    message: str
    details: str = ""
