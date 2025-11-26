"""Custom exception definitions for domain-specific error handling."""
from typing import Any, Optional

class BaseAppException(Exception):
    """Base class for application exceptions with HTTP metadata."""
    status_code: int = 400
    code: str = "error"

    def __init__(self, detail: str, *, payload: Optional[dict[str, Any]] = None):
        super().__init__(detail)
        self.detail = detail
        self.payload = payload or {}

    def to_dict(self) -> dict[str, Any]:
        return {"detail": self.detail, "code": self.code, **self.payload}


class NodeNotFoundException(BaseAppException):
    status_code = 404
    code = "node_not_found"


class DuplicateEraException(BaseAppException):
    status_code = 409
    code = "duplicate_era"


class ValidationException(BaseAppException):
    status_code = 422
    code = "validation_error"
