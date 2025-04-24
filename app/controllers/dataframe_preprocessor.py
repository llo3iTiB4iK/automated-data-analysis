import string
from typing import Any, Callable

import numpy as np
import pandas as pd
from sklearn.preprocessing import MaxAbsScaler, MinMaxScaler, StandardScaler

from app.errors import ParameterError, EmptyDataset
from app.models import PreprocessingParams
from app.models.preprocessing_params import ColumnList


class DataFramePreprocessor:  # todo: refactor this class

    def __init__(self, data: pd.DataFrame) -> None:
        self.data = data

    def _resolve_and_validate_columns(self, columns: ColumnList, param_name: str = "") -> list[str]:
        if columns == "*":
            return self.data.columns.tolist()

        if any(col not in self.data.columns for col in columns):
            raise ParameterError(param_name, str(columns), f"'*' or subset from existing columns ({self.data.columns})")
        return columns

    def _validate_dataset_not_empty(self, operation: str) -> None:
        if self.data.empty:
            raise EmptyDataset(f"The dataset is empty after: {operation.upper()}. "
                               f"Please review your preprocessing parameters.")

    def _apply_str_column_operations(self, columns: ColumnList, transform_fn: callable, apply_to_column: bool = False,
                                     param_name: str = "") -> None:
        columns = self._resolve_and_validate_columns(columns, param_name)
        for col in columns:
            try:
                self.data[col] = transform_fn(self.data[col]) if apply_to_column else self.data[col].apply(transform_fn)
            except (ValueError, AttributeError):
                raise ParameterError(param_name, col,
                                     "A column or list of columns that contain data appropriate for transformation")

    def _fill_missing_values(self, fill_values: Any) -> None:
        self.data.fillna(fill_values, inplace=True)#
        # try:
        #     self.data.fillna(fill_values, inplace=True)
        # except ValueError:
        #     raise PreprocessingParameterError("fill_na_values", str(fill_values), ["JSON object", "string", "number", "boolean"])

    def _fill_missing_with_stat(self) -> None:
        fill_values = {
            col: self.data[col].median() if pd.api.types.is_numeric_dtype(self.data[col])
            else self.data[col].mode().iloc[0]
            for col in self.data.columns if self.data[col].isna().any()
        }
        self._fill_missing_values(fill_values)

    def _select_rows(self, start: int = None, stop: int = None, step: int = None) -> None:
        if start:
            start -= 1
        self.data = self.data.iloc[start:stop:step]
        self._validate_dataset_not_empty("row selection")

    def _find_and_drop_outliers(self, threshold: float) -> None:
        numeric_data = self.data.select_dtypes(include='number')
        z = np.abs((numeric_data - numeric_data.mean()) / numeric_data.std())
        outliers = self.data[(z > threshold).any(axis=1)]
        self.data.drop(outliers.index, inplace=True)

    def _combine_rare_categories(self, category_name: str, category_threshold: float) -> None:
        for col_name in self.data.select_dtypes(include='category').columns:
            category_counts = self.data[col_name].value_counts(normalize=True)
            if not category_threshold:
                category_threshold = category_counts.quantile(0.2)
            rare_categories = category_counts[category_counts <= category_threshold].index
            self.data[col_name] = self.data[col_name].apply(lambda x: category_name if x in rare_categories else x)

    def _scale_numeric_data(self, method: str) -> None:
        scalers: dict = {"max_abs_scaling": MaxAbsScaler, "min_max_scaling": MinMaxScaler, "z_score": StandardScaler}
        numeric_columns: pd.Index = self.data.select_dtypes(include='number').columns
        if numeric_columns.empty:
            return

        self.data[numeric_columns] = scalers[method]().fit_transform(self.data[numeric_columns])

    def preprocess_data(self, params: PreprocessingParams) -> pd.DataFrame:

        def lowercase_columns(cols: ColumnList) -> None:
            self._apply_str_column_operations(cols, lambda s: s.lower() if pd.notna(s) else s,
                                              param_name="case_insensitive_columns")

        def depunct_columns(cols: ColumnList) -> None:
            self._apply_str_column_operations(cols, lambda s: s.translate(str.maketrans('', '', string.punctuation)),
                                              param_name="clear_punct_columns")

        def dedigit_columns(cols: ColumnList) -> None:
            self._apply_str_column_operations(cols, lambda s: s.translate(str.maketrans('', '', string.digits)),
                                              param_name="clear_digits_columns")

        def set_index(cols: ColumnList) -> None:
            self.data.set_index(cols, inplace=True)
            self._validate_dataset_not_empty("setting index")

        def drop_na(axis: str) -> None:
            self.data.dropna(axis=axis, inplace=True)

        def datetime_columns(cols: ColumnList) -> None:
            self._apply_str_column_operations(cols, pd.to_datetime, param_name="datetime_columns")

        def category_columns(cols: ColumnList) -> None:
            self._apply_str_column_operations(
                cols, lambda col: col.astype('category'), apply_to_column=True, param_name="category_columns")

        # A preprocessing pipeline defined as (condition, operation) pairs.
        # Each operation is executed only if its condition is truthy, with the condition passed as an argument.
        pipeline: list[tuple[bool, Callable[..., None]]] = [
            (params.case_insensitive_columns, lowercase_columns),
            (params.clear_punct_columns, depunct_columns),
            (params.clear_digits_columns, dedigit_columns),
            (any([params.row_range_start, params.row_range_end, params.row_range_step]),
             lambda _: self._select_rows(params.row_range_start, params.row_range_end, params.row_range_step)),
            (params.index_cols, set_index),
            (params.fill_na_values, self._fill_missing_values),
            (params.mfill, lambda _: self._fill_missing_with_stat()),
            (params.ffill, lambda _: self.data.ffill(inplace=True)),
            (params.bfill, lambda _: self.data.bfill(inplace=True)),
            (params.drop_na, drop_na),
            (params.drop_outliers, lambda _: self._find_and_drop_outliers(params.outliers_threshold)),
            (params.drop_duplicates, lambda _: self.data.drop_duplicates(
                subset=params.duplicate_subset, keep=params.duplicate_keep, inplace=True)),
            (params.datetime_columns, datetime_columns),
            (params.category_columns, category_columns),
            (params.join_small_cat,
             lambda _: self._combine_rare_categories(params.joined_category_name, params.categories_threshold)),
            (params.scale_numeric, lambda _: self._scale_numeric_data(params.scaling_method))
        ]

        for flag, operation in pipeline:
            if flag:
                operation(flag)

        return self.data
