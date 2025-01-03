import pandas as pd
import numpy as np
from scipy import stats
from sklearn.preprocessing import MaxAbsScaler, MinMaxScaler, StandardScaler
from typing import Any
from services.helpers.validators import check_fillna_dtype_compatibility
from errors import ParameterError

scalers: dict = {"max_abs_scaling": MaxAbsScaler, "min_max_scaling": MinMaxScaler, "z_score": StandardScaler}


def apply_str_column_operations(df: pd.DataFrame, columns: list, transform_fn: callable,
                                apply_to_column: bool = False) -> None:
    for col in columns:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found in the DataFrame.")
        try:
            if apply_to_column:
                df[col] = transform_fn(df[col])
            else:
                df[col] = transform_fn(df[col]) if apply_to_column else df[col].apply(transform_fn)
        except (ValueError, AttributeError):
            raise ValueError(f"Error processing column '{col}'. Ensure the column contains appropriate values.")


def select_rows(df: pd.DataFrame, start: int = None, stop: int = None, step: int = None):
    if start:
        start -= 1
    return df.iloc[start:stop:step]


def fill_missing_values(df: pd.DataFrame, fill_values: Any, allow_type_conversion: bool = False):
    if not allow_type_conversion:
        check_fillna_dtype_compatibility(fill_values, df)
    try:
        df.fillna(fill_values, inplace=True)
    except ValueError:
        raise ParameterError("fill_na_values", str(fill_values), ["JSON object", "string", "number", "boolean"])


def find_and_drop_outliers(df: pd.DataFrame, threshold: float) -> None:
    if not threshold:
        threshold = 3.0
    z: np.ndarray = np.abs(stats.zscore(df.select_dtypes(include=np.number)))
    outliers: pd.DataFrame = df[(z > threshold).any(axis=1)]
    df.drop(outliers.index, inplace=True)


def combine_rare_categories(df: pd.DataFrame, category_name: str, category_threshold: float) -> None:
    if not category_name:
        category_name = "Other"
    for col_name in df.select_dtypes(include='category').columns:
        category_counts = df[col_name].value_counts(normalize=True)
        if not category_threshold:
            category_threshold = category_counts.quantile(0.2)
        rare_categories = category_counts[category_counts <= category_threshold].index
        df[col_name] = df[col_name].apply(lambda x: category_name if x in rare_categories else x)


def scale_numeric_data(df: pd.DataFrame, method: str) -> None:
    scaling_method_values = list(scalers.keys())
    if not method:
        method = scaling_method_values[0]
    numeric_columns: pd.Index = df.select_dtypes(include='number').columns
    if numeric_columns.empty:
        raise ValueError("The dataset has no numeric columns. Please adjust the 'scale_numeric' parameter.")
    if method in scaling_method_values:
        df[numeric_columns] = scalers[method]().fit_transform(df[numeric_columns])
    elif method:
        raise ParameterError("scaling_method", method, scaling_method_values)
