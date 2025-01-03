import pandas as pd
import string
from werkzeug.datastructures.file_storage import FileStorage
from services.helpers import file_operations as fo, data_operations as do, parameter_operations as po, validators as val, process_helpers as ph


def load_and_validate_data(file: FileStorage, params: dict) -> pd.DataFrame:
    extension: str = file.filename.split('.')[-1].lower()
    data: pd.DataFrame = fo.load_data(file, extension, params)
    val.ensure_not_empty(data, "The uploaded file contains no data. Please upload a file with valid data.")
    return data


def apply_column_operations(data: pd.DataFrame, params: dict) -> pd.DataFrame:
    operations = [
        ("case_insensitive_columns", lambda s: s.lower() if pd.notna(s) else s),
        ("clear_punct_columns", lambda s: s.translate(str.maketrans('', '', string.punctuation))),
        ("clear_digits_columns", lambda s: s.translate(str.maketrans('', '', string.digits))),
    ]
    for param_name, operation in operations:
        do.apply_str_column_operations(data, ph.retrieve_columns(data, params, param_name), operation, param_name=param_name)
    return data


def select_rows(data: pd.DataFrame, params: dict) -> pd.DataFrame:
    row_range_params: list = ['row_range_start', 'row_range_end', 'row_range_step']
    selected_rows: list = [ph.retrieve_positive_number(param, params, len(data), int) for param in row_range_params]
    data = do.select_rows(data, *selected_rows)
    val.ensure_not_empty(data, "The specified row range resulted in an empty dataset. Please adjust the range and try again.")
    return data


def set_index(data: pd.DataFrame, params: dict) -> pd.DataFrame:
    po.process_param_with_valid_values("index_col", params, list(data.columns), lambda index_col: data.set_index(index_col, inplace=True))
    return data


def handle_missing_values(data: pd.DataFrame, params: dict) -> pd.DataFrame:
    po.process_json_decoded_param_value('fill_na_values', params, lambda fill_values: do.fill_missing_values(data, fill_values, params.get("allow_type_conversion") == "yes"))
    po.process_param_with_valid_values('ffill', params, ['yes'], lambda _: data.ffill(inplace=True))
    po.process_param_with_valid_values('bfill', params, ['yes'], lambda _: data.bfill(inplace=True))
    po.process_param_with_valid_values("drop_na", params, ['rows', 'columns'], lambda axis: data.dropna(axis=axis, inplace=True))
    val.ensure_not_empty(data, "The dataset is empty after dropping missing values. Please adjust the 'drop_na' parameter or dataset.")
    return data


def handle_outliers_and_duplicates(data: pd.DataFrame, params: dict) -> pd.DataFrame:
    po.process_param_with_valid_values("drop_outliers", params, ['yes'], lambda _: do.find_and_drop_outliers(data, ph.retrieve_positive_number("outliers_threshold", params)))
    po.process_param_with_valid_values("drop_duplicates", params, ['keep_first', 'with_original'], lambda keep_val: data.drop_duplicates(keep=('first' if keep_val == 'keep_first' else False), inplace=True))
    val.ensure_not_empty(data, "The dataset is empty after dropping duplicates. Please adjust the 'drop_duplicates' parameter.")
    return data


def process_specific_column_types(data: pd.DataFrame, params: dict) -> pd.DataFrame:
    do.apply_str_column_operations(data, ph.retrieve_columns(data, params, "datetime_columns"), pd.to_datetime, param_name="datetime_columns")
    do.apply_str_column_operations(data, ph.retrieve_columns(data, params, "category_columns"), lambda col: col.astype('category'), True, param_name="category_columns")
    po.process_param_with_valid_values("join_small_cat", params, ['yes'], lambda _: do.combine_rare_categories(data, params.get("joined_category_name"), ph.retrieve_positive_number("categories_threshold", params, 1)))
    return data


def scale_numeric_data(data: pd.DataFrame, params: dict) -> pd.DataFrame:
    po.process_param_with_valid_values("scale_numeric", params, ['yes'], lambda _: do.scale_numeric_data(data, params.get("scaling_method")))
    return data


def process_data(file: FileStorage, params: dict) -> pd.DataFrame:
    data = load_and_validate_data(file, params)

    pipeline = (
        apply_column_operations,
        select_rows,
        set_index,
        handle_missing_values,
        handle_outliers_and_duplicates,
        process_specific_column_types,
        scale_numeric_data
    )

    for step in pipeline:
        data = step(data, params)

    return data
