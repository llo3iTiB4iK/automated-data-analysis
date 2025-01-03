import pandas as pd
from typing import Any


def ensure_not_empty(data: pd.DataFrame, message: str) -> None:
    if data.empty:
        raise ValueError(message)


def is_convertible(value: str, target_type: type) -> bool:
    try:
        target_type(value)
        return True
    except ValueError:
        return False


def is_positive_number(value: str, max_value: int | float = float('inf'), number_type: type = float) -> int | float:
    return value and is_convertible(value, number_type) and 0 < number_type(value) <= max_value
# def validate_positive_number(param_name: str, params: dict, max_value: int | float = float('inf'), number_type: type = float) -> int | float:
#     value: str = params.get(param_name)
#     if value and is_convertible(value, number_type) and 0 < number_type(value) <= max_value:
#         return number_type(value)
#     elif value:
#         raise ParameterError(param_name, value, [f'Any {number_type} number from interval (0; {str(max_value)}]]'])


def check_fillna_dtype_compatibility(values: dict | int | float | str | bool, df: pd.DataFrame) -> None:
    if not isinstance(values, dict):
        values: dict = {na_col: values for na_col in df.columns[df.isna().any()].tolist()}
    for column, value in values.items():
        if column in df.columns:
            col_type = df[column].dtype
            if pd.api.types.is_numeric_dtype(col_type) and not isinstance(value, (int, float)):
                raise ValueError(f"Value '{value}' cannot be assigned to column '{column}' with numeric type")
            elif pd.api.types.is_string_dtype(col_type) and not isinstance(value, str):
                raise ValueError(f"Value '{value}' cannot be assigned to column '{column}' with string type")
            elif pd.api.types.is_bool_dtype(col_type) and not isinstance(value, bool):
                raise ValueError(f"Value '{value}' cannot be assigned to column '{column}' with boolean type")
        else:
            raise ValueError(f"Column '{column}' to fill missing values is not found in the DataFrame.")


def validate_columns(columns: Any) -> list[str]:
    if isinstance(columns, str):
        return [columns]
    if isinstance(columns, list) and all(isinstance(col, str) for col in columns):
        return columns
    raise TypeError
