import string
from typing import Any, Callable, List

import numpy as np
import pandas as pd
from sklearn.preprocessing import MaxAbsScaler, MinMaxScaler, StandardScaler

from app.errors import ParameterError, EmptyDataset
from app.models.preprocessing_params import ColumnList, PreprocessingParams


class DataFramePreprocessor:
    SCALERS = {
        "max_abs_scaling": MaxAbsScaler,
        "min_max_scaling": MinMaxScaler,
        "z_score": StandardScaler,
    }

    def __init__(self, data: pd.DataFrame) -> None:
        self.data = data

    def preprocess(self, params: PreprocessingParams) -> pd.DataFrame:
        """
        Execute preprocessing steps according to given parameters.
        """
        steps = [
            (params.case_insensitive_columns, self._lowercase_columns),
            (params.clear_punct_columns, self._remove_punctuation),
            (params.clear_digits_columns, self._remove_digits),
            (any([params.row_range_start, params.row_range_end, params.row_range_step]), self._select_rows),
            (params.index_cols, self._set_index),
            (params.fill_na_values is not None, self._fill_missing_values),
            (params.mfill, self._fill_missing_with_median_mode),
            (params.ffill, self._forward_fill),
            (params.bfill, self._backward_fill),
            (params.drop_na, self._drop_na),
            (params.drop_outliers, self._drop_outliers),
            (params.drop_duplicates, self._drop_duplicates),
            (params.datetime_columns, self._convert_datetime),
            (params.category_columns, self._convert_category),
            (params.join_small_cat, self._combine_rare),
            (params.scale_numeric, self._scale_numeric),
        ]

        for condition, action in steps:
            if condition:
                action(params)

        return self.data

    def _resolve_columns(self, cols: ColumnList, param: str) -> List[str]:
        if cols == "*":
            return list(self.data.columns)
        missing = [c for c in cols if c not in self.data.columns]
        if missing:
            raise ParameterError(param, str(cols), f"Available columns: {list(self.data.columns)}")
        return list(cols)

    def _ensure_not_empty(self, step: str) -> None:
        if self.data.empty:
            raise EmptyDataset(f"Dataset empty after {step}")

    # ========== String operations ==========
    def _lowercase_columns(self, params: PreprocessingParams) -> None:
        self._apply_str_op(params.case_insensitive_columns, lambda s: s.lower(), "case_insensitive_columns")

    def _remove_punctuation(self, params: PreprocessingParams) -> None:
        self._apply_str_op(
            params.clear_punct_columns,
            lambda s: s.translate(str.maketrans('', '', string.punctuation)),
            "clear_punct_columns",
        )

    def _remove_digits(self, params: PreprocessingParams) -> None:
        self._apply_str_op(
            params.clear_digits_columns,
            lambda s: s.translate(str.maketrans('', '', string.digits)),
            "clear_digits_columns",
        )

    def _apply_str_op(self, cols: ColumnList, func: Callable[[Any], Any], param: str) -> None:
        columns = self._resolve_columns(cols, param)
        for col in columns:
            try:
                self.data[col] = self.data[col].apply(lambda x: func(x) if pd.notna(x) else x)
            except Exception:
                raise ParameterError(param, col, "Invalid operation on column")

    # ========== Row/Index operations ==========
    def _select_rows(self, params: PreprocessingParams) -> None:
        start = (params.row_range_start or 1) - 1
        stop = params.row_range_end
        step = params.row_range_step
        self.data = self.data.iloc[start:stop:step]
        self._ensure_not_empty("row_selection")

    def _set_index(self, params: PreprocessingParams) -> None:
        cols = self._resolve_columns(params.index_cols, "index_cols")
        self.data.set_index(cols, inplace=True)
        self._ensure_not_empty("set_index")

    # ========== Missing value operations ==========
    def _fill_missing_values(self, params: PreprocessingParams) -> None:
        try:
            self.data.fillna(params.fill_na_values, inplace=True)
        except Exception:
            raise ParameterError("fill_na_values", str(params.fill_na_values), "scalar or dict mapping")

    def _fill_missing_with_median_mode(self, _: PreprocessingParams) -> None:
        stats = {}
        for col in self.data.columns:
            if self.data[col].isna().any():
                stats[col] = (
                    self.data[col].median()
                    if pd.api.types.is_numeric_dtype(self.data[col])
                    else self.data[col].mode().iloc[0]
                )
        self.data.fillna(stats, inplace=True)

    def _forward_fill(self, _: PreprocessingParams) -> None:
        self.data.ffill(inplace=True)

    def _backward_fill(self, _: PreprocessingParams) -> None:
        self.data.bfill(inplace=True)

    def _drop_na(self, params: PreprocessingParams) -> None:
        self.data.dropna(axis=params.drop_na, inplace=True)
        self._ensure_not_empty("drop_missing_values")

    # ========== Outliers & duplicates ==========
    def _drop_outliers(self, params: PreprocessingParams) -> None:
        num = self.data.select_dtypes(include='number')
        z: pd.DataFrame = np.abs((num - num.mean()) / num.std())
        mask = (z > params.outliers_threshold).any(axis=1)
        self.data = self.data.loc[~mask]
        self._ensure_not_empty("drop_outliers")

    def _drop_duplicates(self, params: PreprocessingParams) -> None:
        subset = None if not params.duplicate_subset else self._resolve_columns(params.duplicate_subset, "duplicate_subset")
        self.data.drop_duplicates(subset=subset, keep=params.duplicate_keep, inplace=True)
        self._ensure_not_empty("drop_duplicates")

    # ========== Type conversions ==========
    def _convert_datetime(self, params: PreprocessingParams) -> None:
        self._apply_generic_op(params.datetime_columns, pd.to_datetime, "datetime_columns")

    def _convert_category(self, params: PreprocessingParams) -> None:
        self._apply_generic_op(params.category_columns, lambda col: col.astype('category'), "category_columns", apply_to_column=True)

    def _apply_generic_op(
        self, cols: ColumnList, func: Callable[..., Any], param: str, apply_to_column: bool = False
    ) -> None:
        columns = self._resolve_columns(cols, param)
        for col in columns:
            try:
                self.data[col] = func(self.data[col]) if apply_to_column else self.data[col].apply(func)
            except Exception:
                raise ParameterError(param, col, "Columns, appropriate for transformation")

    # ========== Category merging ==========
    def _combine_rare(self, params: PreprocessingParams) -> None:
        for col in self.data.select_dtypes(include='category').columns:
            counts = self.data[col].value_counts(normalize=True)
            threshold = params.categories_threshold or counts.quantile(0.2)
            rare_ = counts[counts <= threshold].index
            self.data[col] = self.data[col].apply(lambda x, rare=rare_: params.joined_category_name if x in rare else x)

    # ========== Scaling ==========
    def _scale_numeric(self, params: PreprocessingParams) -> None:
        cols = self.data.select_dtypes(include='number').columns
        if not cols.any():
            return
        scaler = self.SCALERS[params.scaling_method]()
        self.data[cols] = scaler.fit_transform(self.data[cols])
