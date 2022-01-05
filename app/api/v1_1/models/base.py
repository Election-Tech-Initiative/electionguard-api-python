from typing import Any, Optional
from enum import Enum
from pydantic import BaseModel

__all__ = [
    "Base",
    "BaseRequest",
    "BaseResponse",
    "BaseQueryRequest",
    "BaseValidationRequest",
    "BaseValidationResponse",
    "ResponseStatus",
]

Schema = Any


class ResponseStatus(str, Enum):
    FAIL = "fail"
    SUCCESS = "success"


class Base(BaseModel):
    "A basic model object"


class BaseRequest(BaseModel):
    """A basic request"""


class BaseResponse(BaseModel):
    """A basic response"""

    status: ResponseStatus = ResponseStatus.SUCCESS
    """The status of the response"""

    message: Optional[str] = None
    """An optional message describing the response"""

    def is_success(self) -> bool:
        return self.status == ResponseStatus.SUCCESS


class BaseQueryRequest(BaseRequest):
    """Find something"""

    filter: Optional[Any] = None


class BaseValidationRequest(BaseRequest):
    """Base validation request"""

    schema_override: Optional[Schema] = None
    """Optionally specify a schema to validate against"""


class BaseValidationResponse(BaseResponse):
    """Response for validating models"""

    details: Optional[str] = None
    """Optional details of the validation result"""
