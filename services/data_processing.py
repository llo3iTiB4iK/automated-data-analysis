import pandas as pd
import numpy as np
from scipy import stats
import sqlite3
import tempfile
import os
from werkzeug.datastructures.file_storage import FileStorage
from errors import ParameterError

drop_na_values: list = ['rows', 'columns']
drop_duplicates_values: list = ['keep_first', 'with_original']
drop_outliers_values: list = ['yes']


def process_data(file: FileStorage, params: dict) -> pd.DataFrame:
    # Determine file extension
    extension: str = file.filename.split('.')[-1].lower()

    # Read data based on file extension
    data: pd.DataFrame
    if extension == 'csv':
        optional_params: list = ["sep", "thousands", "decimal"]
        read_csv_kwargs: dict = {param: params[param] for param in optional_params if params.get(param)}
        data = pd.read_csv(file.stream, **read_csv_kwargs)
    elif extension in ['xls', 'xlsx']:
        optional_params: list = ["sheet_name", "thousands", "decimal"]
        read_excel_params: dict = {param: params[param] for param in optional_params if params.get(param)}
        data = pd.read_excel(file.stream.read(), **read_excel_params)
    elif extension == 'json':
        data = pd.read_json(file.stream)
    elif extension == 'db':
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp_file:
            tmp_file.write(file.read())
            temp_file_path: str = tmp_file.name
        cnx: sqlite3.Connection = sqlite3.connect(temp_file_path)
        table_name: str = params['table_name']
        try:
            data = pd.read_sql(f"SELECT * FROM {table_name}", cnx)
        except pd.errors.DatabaseError:
            cursor: sqlite3.Cursor = cnx.execute("SELECT name FROM sqlite_master WHERE type='table';")
            existing_tables: list = [record[0] for record in cursor.fetchall()]
            raise ParameterError('table_name', table_name, existing_tables)
        finally:
            cnx.close()
            os.remove(temp_file_path)
    else:
        raise ValueError("Unsupported file format. Please upload CSV, Excel, or JSON files.")
    if data.empty:
        raise ValueError("The uploaded file contains no data. Please upload a file with valid data.")

    # Limit row range on demand
    def validate_row_range(param_name: str, params: dict, max_value: int) -> int:
        value: str = params.get(param_name)
        if value and value.isdigit() and 1 <= int(value) <= max_value:
            return int(value)
        elif value:
            raise ParameterError(param_name, value, ['1', '...', str(max_value)])

    row_range_start: int = validate_row_range('row_range_start', params, len(data))
    row_range_end: int = validate_row_range('row_range_end', params, len(data))
    row_range_step: int = validate_row_range('row_range_step', params, len(data))
    if row_range_start:
        row_range_start -= 1
    data = data.iloc[row_range_start:row_range_end:row_range_step]
    if data.empty:
        raise ValueError("The specified row range resulted in an empty dataset. Please adjust the range and try again.")

    # Set index on demand
    index_col: str = params.get('index_col')
    if index_col in data.columns.values:
        data.set_index(index_col, inplace=True)
        if data.empty:
            raise ValueError("The dataset is empty after setting the index. Please check the selected index column.")
    elif index_col:
        raise ParameterError('index_col', index_col, list(data.columns.values))

    # Drop missing values on demand
    drop_na: str = params.get('drop_na')
    if drop_na in drop_na_values:
        data.dropna(axis=params.get('drop_na'), inplace=True)
        if data.empty:
            raise ValueError(
                "The dataset is empty after dropping missing values. Please adjust the drop_na parameter or dataset.")
    elif drop_na:
        raise ParameterError('drop_na', drop_na, drop_na_values)

    # Fill missing values on demand
    # todo 2: add filling NaN values

    # Drop outliers on demand
    def is_float(string):
        try:
            float(string)
            return True
        except ValueError:
            return False

    def validate_outliers_threshold(param_name: str, params: dict, max_value: float) -> float:
        value: str = params.get(param_name)
        if value and is_float(value) and 0 < float(value):
            return float(value)
        elif value:
            raise ParameterError(param_name, value, ['0+', '...', str(max_value)])

    def find_and_drop_outliers(df: pd.DataFrame, threshold: float) -> None:
        if not threshold:
            threshold = 3.0
        z: np.ndarray = np.abs(stats.zscore(df.select_dtypes(include=np.number)))
        outliers: pd.DataFrame = df[(z > threshold).any(axis=1)]
        df.drop(outliers.index, inplace=True)

    drop_outliers: str = params.get('drop_outliers')
    if drop_outliers in drop_outliers_values:
        find_and_drop_outliers(data, validate_outliers_threshold("outliers_threshold", params, float('inf')))
    elif drop_outliers:
        raise ParameterError('drop_outliers', drop_outliers, drop_outliers_values)

    # Drop duplicates on demand
    drop_duplicates: str = params.get('drop_duplicates')
    if drop_duplicates in drop_duplicates_values:
        data.drop_duplicates(keep=('first' if drop_duplicates == drop_duplicates_values[0] else False), inplace=True)
        if data.empty:
            raise ValueError(
                "The dataset is empty after dropping duplicates. Please adjust the drop_duplicates parameter.")
    elif drop_duplicates:
        raise ParameterError('drop_duplicates', drop_duplicates, drop_duplicates_values)

    # Convert data types on demand
    # todo 5: add type conversion

    # Convert text data on demand
    # todo 6: add text data conversion

    # Process categorical variables on demand
    # todo 7: add categorical variables processing
    # Using the "one-hot encoding" or "label encoding" method to convert categorical variables into numeric formats.
    # Об'єднання рідких категорій або категорій, які мають мало спостережень, у одну категорію.

    # Scale numeric data on demand
    # todo 8: add numeric data scaling

    return data
# todo 1: refactor code
