import pandas as pd
from services.helpers.dataframe_preprocessor import DataFramePreprocessor


def process_data(data: pd.DataFrame, params: dict) -> pd.DataFrame:
    preprocessor: DataFramePreprocessor = DataFramePreprocessor(data, params)
    pipeline: tuple = (
        preprocessor.apply_column_operations,
        preprocessor.select_rows,
        preprocessor.set_index,
        preprocessor.handle_missing_values,
        preprocessor.handle_outliers_and_duplicates,
        preprocessor.process_specific_column_types,
        preprocessor.scale_numeric_data
    )
    for step in pipeline:
        step()

    return preprocessor.data
