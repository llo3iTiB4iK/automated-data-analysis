import pandas as pd
import string
from services.helpers import data_operations as do, parameter_operations as po, validators as val, process_helpers as ph


class DataFramePreprocessor:

    def __init__(self, data: pd.DataFrame, params: dict):
        self.data: pd.DataFrame = data
        self.params: dict = params

    def apply_column_operations(self) -> None:
        operations = [
            ("case_insensitive_columns", lambda s: s.lower() if pd.notna(s) else s),
            ("clear_punct_columns", lambda s: s.translate(str.maketrans('', '', string.punctuation))),
            ("clear_digits_columns", lambda s: s.translate(str.maketrans('', '', string.digits))),
        ]
        for param_name, operation in operations:
            do.apply_str_column_operations(self.data, ph.retrieve_columns(self.data, self.params, param_name),
                                           operation, param_name=param_name)

    def select_rows(self) -> None:
        row_range_params: list = ['row_range_start', 'row_range_end', 'row_range_step']
        selected_rows: list = [ph.retrieve_positive_number(param, self.params, len(self.data), int)
                               for param in row_range_params]
        data = do.select_rows(self.data, *selected_rows)
        val.ensure_not_empty(data, "The specified row range resulted in an empty dataset. "
                                   "Please adjust the range and try again.")
        self.data = data

    def set_index(self) -> None:
        po.process_param_with_valid_values("index_col", self.params, list(self.data.columns),
                                           lambda index_col: self.data.set_index(index_col, inplace=True))

    def handle_missing_values(self) -> None:
        po.process_json_decoded_param_value('fill_na_values', self.params, lambda fill_values: do.fill_missing_values(
            self.data, fill_values, self.params.get("allow_type_conversion") == "yes"))
        po.process_param_with_valid_values('ffill', self.params, ['yes'], lambda _: self.data.ffill(inplace=True))
        po.process_param_with_valid_values('bfill', self.params, ['yes'], lambda _: self.data.bfill(inplace=True))
        po.process_param_with_valid_values("drop_na", self.params, ['rows', 'columns'],
                                           lambda axis: self.data.dropna(axis=axis, inplace=True))
        val.ensure_not_empty(self.data, "The dataset is empty after dropping missing values. "
                                        "Please adjust the 'drop_na' parameter or dataset.")

    def handle_outliers_and_duplicates(self) -> None:
        po.process_param_with_valid_values("drop_outliers", self.params, ['yes'], lambda _: do.find_and_drop_outliers(
            self.data, ph.retrieve_positive_number("outliers_threshold", self.params)))
        po.process_param_with_valid_values("drop_duplicates", self.params, ['keep_first', 'with_original'], lambda
            keep_val: self.data.drop_duplicates(keep=('first' if keep_val == 'keep_first' else False), inplace=True))
        val.ensure_not_empty(self.data, "The dataset is empty after dropping duplicates. "
                                        "Please adjust the 'drop_duplicates' parameter.")

    def process_specific_column_types(self) -> None:
        do.apply_str_column_operations(self.data, ph.retrieve_columns(self.data, self.params, "datetime_columns"),
                                       pd.to_datetime, param_name="datetime_columns")
        do.apply_str_column_operations(self.data, ph.retrieve_columns(self.data, self.params, "category_columns"),
                                       lambda col: col.astype('category'), True, param_name="category_columns")
        po.process_param_with_valid_values("join_small_cat", self.params, ['yes'], lambda _: do.combine_rare_categories(
            self.data, self.params.get("joined_category_name"),
            ph.retrieve_positive_number("categories_threshold", self.params, 1)))

    def scale_numeric_data(self) -> None:
        po.process_param_with_valid_values("scale_numeric", self.params, ['yes'], lambda _: do.scale_numeric_data(
            self.data, self.params.get("scaling_method")))
