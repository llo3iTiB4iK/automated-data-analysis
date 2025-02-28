import pandas as pd
from services.helpers.dataframe_preprocessor import DataFramePreprocessor, scalers
from services.helpers.parameter_operations import ParameterOperations


def process_data(data: pd.DataFrame, raw_params: dict) -> pd.DataFrame:
    params: ParameterOperations = ParameterOperations(raw_params)
    preprocessor: DataFramePreprocessor = DataFramePreprocessor(data)
    return preprocessor.preprocess_data(
        case_insensitive_columns=params.retrieve_columns(data, "case_insensitive_columns"),
        clear_punct_columns=params.retrieve_columns(data, "clear_punct_columns"),
        clear_digits_columns=params.retrieve_columns(data, "clear_digits_columns"),
        row_range_start=params.get_positive_number_value("row_range_start", len(data), int),
        row_range_end=params.get_positive_number_value("row_range_end", len(data), int),
        row_range_step=params.get_positive_number_value("row_range_step", len(data), int),
        index_cols=params.retrieve_columns(data, "index_cols"),
        fill_na_values=params.get_json_value("fill_na_values"),
        allow_type_conversion=params.get_bool_value("allow_type_conversion"),
        ffill=params.get_bool_value("ffill"),
        bfill=params.get_bool_value("bfill"),
        drop_na=params.get_value_among_valid("drop_na", ["rows", "columns"]),
        drop_outliers=params.get_bool_value("drop_outliers"),
        outliers_threshold=params.get_positive_number_value("outliers_threshold"),
        drop_duplicates=params.get_value_among_valid("drop_duplicates", ['keep_first', 'with_original']),
        datetime_columns=params.retrieve_columns(data, "datetime_columns"),
        category_columns=params.retrieve_columns(data, "category_columns"),
        join_small_cat=params.get_bool_value("join_small_cat"),
        joined_category_name=params.get_str_value("joined_category_name"),
        categories_threshold=params.get_positive_number_value("categories_threshold", 1),
        scale_numeric=params.get_bool_value("scale_numeric"),
        scaling_method=params.get_value_among_valid("scaling_method", list(scalers.keys())))
