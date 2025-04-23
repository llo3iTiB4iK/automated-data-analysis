from .base_error import BaseError


class ParameterMissing(BaseError):

    def __init__(self, param_name: str) -> None:
        self.param = param_name

    def to_dict(self) -> dict[str, str]:
        return {
            "error": "Missing required parameter",
            "parameter": self.param,
        }
