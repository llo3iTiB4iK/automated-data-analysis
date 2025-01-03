from typing import Any
import json
from errors import ParameterError


def process_param_with_valid_values(param_name: str, params: dict, valid_values: list, operation: callable) -> Any:
    param_value: str = params.get(param_name)
    if param_value in valid_values:
        return operation(param_value)
    elif param_value:
        raise ParameterError(param_name, param_value, valid_values)


def get_processed_param_value_with_condition(param_name: str, params: dict, valid_values: list, condition: callable, operation: callable) -> Any:
    value: str = params.get(param_name)
    if condition(value):
        return operation(value)
    if value:
        raise ParameterError(param_name, value, valid_values)


def process_json_decoded_param_value(param_name: str, params: dict, operation: callable) -> Any:
    json_str: str = params.get(param_name)
    if json_str:
        try:
            json_obj = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error occurred when decoding provided JSON for \"{param_name}\" parameter: \"{e}\"")
        else:
            return operation(json_obj)
