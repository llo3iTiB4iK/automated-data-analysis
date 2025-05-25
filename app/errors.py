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

    def __init__(self, filename: str, message: str = "") -> None:
        description = {
            "message": "An error occurred while reading provided data file",
            "file": filename,
            "details": message
        }
        super().__init__(description=description)


class TransformationError(UnprocessableEntity):
    name = "Transformation Error"

    def __init__(self, operation: str, column: str) -> None:
        description = {
            "message": "Failed to apply transformation to column",
            "transformation": operation,
            "column": column
        }
        super().__init__(description=description)


class ColumnNotFound(UnprocessableEntity):
    name = "Column Not Found"

    def __init__(self, missing: list[str], available: list[str]) -> None:
        description = {
            "message": "Requested columns are not present in the dataset",
            "missing_columns": missing,
            "available_columns": available
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
