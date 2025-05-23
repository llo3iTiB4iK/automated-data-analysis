from typing import Any

from werkzeug.exceptions import BadRequest, UnprocessableEntity


class ParameterError(BadRequest):
    name = "Invalid Parameter"

    def __init__(self, param_name: str, value: str, expected: Any) -> None:
        description = {
            "message": "Invalid value provided for request parameter",
            "parameter": param_name,
            "invalid_value": value,
            "expected_values": expected
        }
        super().__init__(description=description)


class ParameterMissing(BadRequest):
    name = "Missing Parameter"

    def __init__(self, param_name: str) -> None:
        description = {
            "message": "Missing required request parameter",
            "parameter": param_name
        }
        super().__init__(description=description)


class ReadingError(UnprocessableEntity):
    name = "Reading Error"

    def __init__(self, filename: str) -> None:
        description = {
            "message": "An error occurred while reading provided data file",
            "file": filename
        }
        super().__init__(description=description)


class EmptyDataset(UnprocessableEntity):
    name = "Empty Dataset"

    def __init__(self, msg: str) -> None:
        super().__init__(description=msg)


class ValidationFailed(UnprocessableEntity):
    name = "Validation Failed"

    def __init__(self, errors: list[dict[str, Any]]) -> None:
        super().__init__(description=errors)
