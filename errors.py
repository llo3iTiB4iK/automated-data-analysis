
class ParameterError(ValueError):
    def __init__(self, parameter: str, value: str, allowed_values: list) -> None:
        message = f"Incorrect value for parameter '{parameter}': '{value}'. Allowed values are: {allowed_values}."
        super().__init__(message)
