import pandas as pd
import numpy as np
from sklearn.preprocessing import MaxAbsScaler, MinMaxScaler, StandardScaler
import string
from typing import Any
from errors import ParameterError

scalers: dict = {"max_abs_scaling": MaxAbsScaler, "min_max_scaling": MinMaxScaler, "z_score": StandardScaler}


class DataFramePreprocessor:

    def __init__(self, data: pd.DataFrame):
        self.data: pd.DataFrame = data

    def __check_fillna_dtype_compatibility(self, values: dict | int | float | str | bool) -> None:
        if not isinstance(values, dict):
            values: dict = {na_col: values for na_col in self.data.columns[self.data.isna().any()].tolist()}
        for column, value in values.items():
            if column in self.data.columns:
                col_type = self.data[column].dtype
                if pd.api.types.is_numeric_dtype(col_type) and not isinstance(value, (int, float)):
                    raise ValueError(f"Value '{value}' cannot be assigned to column '{column}' with numeric type")
                elif pd.api.types.is_string_dtype(col_type) and not isinstance(value, str):
                    raise ValueError(f"Value '{value}' cannot be assigned to column '{column}' with string type")
                elif pd.api.types.is_bool_dtype(col_type) and not isinstance(value, bool):
                    raise ValueError(f"Value '{value}' cannot be assigned to column '{column}' with boolean type")
            else:
                raise ValueError(f"Column '{column}' to fill missing values is not found in the DataFrame.")

    def _apply_str_column_operations(self, columns: list, transform_fn: callable, apply_to_column: bool = False,
                                     param_name: str = "") -> None:
        for col in columns:
            if col not in self.data.columns:
                raise ValueError(f"Column '{col}' not found in the DataFrame.")
            try:
                self.data[col] = transform_fn(self.data[col]) if apply_to_column else self.data[col].apply(transform_fn)
            except (ValueError, AttributeError):
                raise ParameterError(param_name, str(columns), ["A column or list of columns that contain data, appropriate for transformation"])

    def _fill_missing_values(self, fill_values: Any, allow_type_conversion: bool = False):
        if not allow_type_conversion:
            self.__check_fillna_dtype_compatibility(fill_values)
        try:
            self.data.fillna(fill_values, inplace=True)
        except ValueError:
            raise ParameterError("fill_na_values", str(fill_values), ["JSON object", "string", "number", "boolean"])

    def _select_rows(self, start: int = None, stop: int = None, step: int = None):
        if start:
            start -= 1
        self.data = self.data.iloc[start:stop:step]
        if self.data.empty:
            raise ValueError("The specified row range resulted in an empty dataset. Please adjust the range and try again.")

    def _find_and_drop_outliers(self, threshold: float) -> None:
        if not threshold:
            threshold = 3.0
        numeric_data: pd.DataFrame = self.data.select_dtypes(include='number')
        z: np.ndarray = np.abs((numeric_data - numeric_data.mean()) / numeric_data.std())
        outliers: pd.DataFrame = self.data[(z > threshold).any(axis=1)]
        self.data.drop(outliers.index, inplace=True)

    def _combine_rare_categories(self, category_name: str, category_threshold: float) -> None:
        if not category_name:
            category_name = "Other"
        for col_name in self.data.select_dtypes(include='category').columns:
            category_counts = self.data[col_name].value_counts(normalize=True)
            if not category_threshold:
                category_threshold = category_counts.quantile(0.2)
            rare_categories = category_counts[category_counts <= category_threshold].index
            self.data[col_name] = self.data[col_name].apply(lambda x: category_name if x in rare_categories else x)

    def _scale_numeric_data(self, method: str) -> None:
        scaling_method_values = list(scalers.keys())
        if not method:
            method = scaling_method_values[0]
        numeric_columns: pd.Index = self.data.select_dtypes(include='number').columns
        if numeric_columns.empty:
            raise ValueError("The dataset has no numeric columns. Please adjust the 'scale_numeric' parameter.")
        self.data[numeric_columns] = scalers[method]().fit_transform(self.data[numeric_columns])

    def preprocess_data(self, case_insensitive_columns: list = None, clear_punct_columns: list = None,
                        clear_digits_columns: list = None, row_range_start: int = None, row_range_end: int = None,
                        row_range_step: int = None, index_cols: list = None, fill_na_values: Any = None,
                        allow_type_conversion: bool = False, ffill: bool = False, bfill: bool = False,
                        drop_na: str = None, drop_outliers: bool = False, outliers_threshold: float = 3.0,
                        drop_duplicates: str = None, datetime_columns: list = None, category_columns: list = None,
                        join_small_cat: bool = False, joined_category_name: str = "Other", categories_threshold: float = None,
                        scale_numeric: bool = False, scaling_method: str = None) -> pd.DataFrame:

        # String columns operations
        str_operations = [
            (case_insensitive_columns, lambda s: s.lower() if pd.notna(s) else s, "case_insensitive_columns"),
            (clear_punct_columns, lambda s: s.translate(str.maketrans('', '', string.punctuation)), "clear_punct_columns"),
            (clear_digits_columns, lambda s: s.translate(str.maketrans('', '', string.digits)), "clear_digits_columns"),
        ]
        for columns, operation, param_name in str_operations:
            if columns:
                self._apply_str_column_operations(columns, operation, param_name=param_name)

        # Row selection
        if any([row_range_start, row_range_end, row_range_step]):
            self._select_rows(row_range_start, row_range_end, row_range_step)

        # Index handling
        if index_cols:
            self.data.set_index(index_cols, inplace=True)

        # Handling missing values
        if fill_na_values:
            self._fill_missing_values(fill_na_values, allow_type_conversion)
        if ffill:
            self.data.ffill(inplace=True)
        if bfill:
            self.data.bfill(inplace=True)
        if drop_na:
            self.data.dropna(axis=drop_na, inplace=True)
            if self.data.empty:
                raise ValueError("The dataset is empty after dropping missing values. Please adjust the 'drop_na' parameter or dataset.")

        # Handling outliers
        if drop_outliers:
            self._find_and_drop_outliers(outliers_threshold)

        # Handling duplicates
        if drop_duplicates:
            keep_strategy = 'first' if drop_duplicates == 'keep_first' else False
            self.data.drop_duplicates(keep=keep_strategy, inplace=True)
            if self.data.empty:
                raise ValueError("The dataset is empty after dropping duplicates. Adjust the 'drop_duplicates' parameter.")

        # Processing specific type columns
        if datetime_columns:
            self._apply_str_column_operations(datetime_columns, pd.to_datetime, param_name="datetime_columns")
        if category_columns:
            self._apply_str_column_operations(category_columns, lambda col: col.astype('category'), True, "category_columns")

        # Joining small data categories
        if join_small_cat:
            self._combine_rare_categories(joined_category_name, categories_threshold)

        # Numeric data scaling
        if scale_numeric:
            self._scale_numeric_data(scaling_method)

        return self.data
