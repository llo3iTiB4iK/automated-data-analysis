from pydantic import ValidationError
from .base_error import BaseError


class PydanticValidationError(BaseError):
    def __init__(self, error: ValidationError):
        self.error = error

    def to_dict(self):
        return {
            "error": "Validation error",
            "details": self.error.errors()
        }
