from pydantic import ValidationError

from .base_error import BaseError


class PydanticValidationError(BaseError):
    def __init__(self, error: ValidationError) -> None:
        self.error = error

    def to_dict(self) -> dict[str, str | list]:
        simplified_errors = [
            {
                "parameter": err["loc"][0],
                "message": err["msg"],
                "value": err["input"]
            }
            for err in self.error.errors()
        ]
        return {
            "error": "Validation error",
            "details": simplified_errors
        }
