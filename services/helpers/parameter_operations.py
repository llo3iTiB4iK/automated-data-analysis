from typing import Any
import json
import pandas as pd
from errors import ParameterError


class ParameterOperations(dict):

    def __init__(self, params: dict):
        super().__init__(params)

    def get_str_value(self, param_name: str, default: str = None) -> str:
        param_value: str = self.get(param_name)
        return param_value if param_value and param_value.strip() else default

    def get_value_among_valid(self, param_name: str, valid_values: list) -> str:
        param_value: str = self.get_str_value(param_name)
        if param_value is None or param_value in valid_values:
            return param_value
        raise ParameterError(param_name, param_value, valid_values)

    def get_bool_value(self, param_name: str) -> bool:
        return self.get_value_among_valid(param_name, ['yes']) == 'yes'

    def get_json_value(self, param_name: str) -> Any:
        json_str: str = self.get(param_name)
        if not json_str:
            return None
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error decoding JSON for parameter\"{param_name}\": \"{e}\"")

    def get_positive_number_value(self, param_name: str, max_value: int | float = float('inf'),
                                  number_type: type = float) -> None | int | float:
        numeric_str: str = self.get(param_name)
        if not numeric_str:
            return None
        try:
            converted_num: int | float = number_type(numeric_str)
            if 0 < converted_num <= max_value:
                return converted_num
        except ValueError:
            pass
        raise ParameterError(param_name, numeric_str, [f"{number_type.__name__} in range (0, {max_value}]"])

    def retrieve_columns(self, data: pd.DataFrame, columns_key: str) -> list:
        columns_param: str = self.get(columns_key)
        if not columns_param:
            return None
        if columns_param == '*':
            return data.columns.tolist()

        columns = self.get_json_value(columns_key)
        if isinstance(columns, str):
            return [columns]
        if isinstance(columns, list) and all(isinstance(col, str) for col in columns):
            return columns

        raise ParameterError(columns_key, columns_param, ["string", "array[string]", "*"])
