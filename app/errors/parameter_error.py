from typing import Any
from .base_error import BaseError


class ParameterError(BaseError):

    def __init__(self, param_name: str, value: str, expected: Any) -> None:
        self.param = param_name
        self.value = value
        self.expected = expected

    def to_dict(self) -> dict[str, Any]:
        return {
            "error": "Invalid parameter",
            "parameter": self.param,
            "invalid_value": self.value,
            "expected_values": self.expected
        }
