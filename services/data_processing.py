import pandas as pd
import numpy as np
from scipy import stats
from sklearn.preprocessing import MaxAbsScaler, MinMaxScaler, StandardScaler
import sqlite3
import tempfile
import os
import json
import string
from typing import Any
from werkzeug.datastructures.file_storage import FileStorage
from errors import ParameterError

drop_na_values: list = ['rows', 'columns']
drop_duplicates_values: list = ['keep_first', 'with_original']
drop_outliers_values: list = ['yes']
join_small_cat_values: list = ['yes']
scale_numeric_values: list = ['yes']
scalers: dict = {"max_abs_scaling": MaxAbsScaler, "min_max_scaling": MinMaxScaler, "z_score": StandardScaler}


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

    # Perform basic text data unification on demand
    case_insensitive_columns: str = params.get("case_insensitive_columns")
    if case_insensitive_columns:
        try:
            case_insensitive_columns_decoded: Any = json.loads(case_insensitive_columns)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error occurred when decoding provided JSON: \"{e}\"")

        if isinstance(case_insensitive_columns_decoded, str):
            case_insensitive_columns_decoded: list = [case_insensitive_columns_decoded]
        try:
            for col in case_insensitive_columns_decoded:
                if not isinstance(col, str):
                    raise TypeError
                try:
                    data[col] = data[col].str.lower()
                except KeyError:
                    raise ValueError(f"Column '{col}' to convert into lowercase is not found in the DataFrame.")
                except AttributeError:
                    raise ValueError(f"Column '{col}' could not be converted into lowercase. Ensure the column contains"
                                     f" string values.")
        except TypeError:
            raise ParameterError("case_insensitive_columns", case_insensitive_columns, ["string", "array[string]"])

    clear_punct_columns: str = params.get("clear_punct_columns")
    if clear_punct_columns:
        try:
            clear_punct_columns_decoded: Any = json.loads(clear_punct_columns)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error occurred when decoding provided JSON: \"{e}\"")

        if isinstance(clear_punct_columns_decoded, str):
            clear_punct_columns_decoded: list = [clear_punct_columns_decoded]
        try:
            for col in clear_punct_columns_decoded:
                if not isinstance(col, str):
                    raise TypeError
                try:
                    data[col] = data[col].apply(lambda s: s.translate(s.maketrans("", "", string.punctuation)))
                except KeyError:
                    raise ValueError(f"Column '{col}' to remove punctuation is not found in the DataFrame.")
                except AttributeError:
                    raise ValueError(f"Column '{col}' could not be stripped of punctuation. Ensure the column contains"
                                     f" string values.")
        except TypeError:
            raise ParameterError("clear_punct_columns", clear_punct_columns, ["string", "array[string]"])

    clear_digits_columns: str = params.get("clear_digits_columns")
    if clear_digits_columns:
        try:
            clear_digits_columns_decoded: Any = json.loads(clear_digits_columns)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error occurred when decoding provided JSON: \"{e}\"")

        if isinstance(clear_digits_columns_decoded, str):
            clear_digits_columns_decoded: list = [clear_digits_columns_decoded]
        try:
            for col in clear_digits_columns_decoded:
                if not isinstance(col, str):
                    raise TypeError
                try:
                    data[col] = data[col].apply(lambda s: s.translate(s.maketrans("", "", string.digits)))
                except KeyError:
                    raise ValueError(f"Column '{col}' to remove digits is not found in the DataFrame.")
                except AttributeError:
                    raise ValueError(f"Column '{col}' could not be stripped of digits. Ensure the column contains "
                                     f"string values.")
        except TypeError:
            raise ParameterError("clear_digits_columns", clear_digits_columns, ["string", "array[string]"])

    # Set index on demand
    index_col: str = params.get('index_col')
    if index_col in data.columns.values:
        data.set_index(index_col, inplace=True)
        if data.empty:
            raise ValueError("The dataset is empty after setting the index. Please check the selected index column.")
    elif index_col:
        raise ParameterError('index_col', index_col, list(data.columns.values))

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

    # Fill missing values on demand
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

    fill_na_values: str = params.get('fill_na_values')
    if fill_na_values:
        try:
            fill_na_decoded: Any = json.loads(fill_na_values)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error occurred when decoding provided JSON: \"{e}\"")

        if params.get("allow_type_conversion") != "true":
            check_fillna_dtype_compatibility(fill_na_decoded, data)
        try:
            data.fillna(fill_na_decoded, inplace=True)
        except (ValueError, TypeError):
            raise ParameterError("fill_na_values", fill_na_values, ["JSON object", "string", "number", "boolean"])

    if params.get('ffill') == 'true':
        data.ffill(inplace=True)
    if params.get('bfill') == 'true':
        data.bfill(inplace=True)

    # Drop missing values on demand
    drop_na: str = params.get('drop_na')
    if drop_na in drop_na_values:
        data.dropna(axis=params.get('drop_na'), inplace=True)
        if data.empty:
            raise ValueError(
                "The dataset is empty after dropping missing values. Please adjust the 'drop_na' parameter or dataset.")
    elif drop_na:
        raise ParameterError('drop_na', drop_na, drop_na_values)

    # Drop outliers on demand
    def is_float(string: str) -> bool:
        try:
            float(string)
            return True
        except ValueError:
            return False

    def validate_positive_float_threshold(param_name: str, params: dict, max_value: float) -> float:
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
        find_and_drop_outliers(data, validate_positive_float_threshold("outliers_threshold", params, float('inf')))
    elif drop_outliers:
        raise ParameterError('drop_outliers', drop_outliers, drop_outliers_values)

    # Drop duplicates on demand
    drop_duplicates: str = params.get('drop_duplicates')
    if drop_duplicates in drop_duplicates_values:
        data.drop_duplicates(keep=('first' if drop_duplicates == drop_duplicates_values[0] else False), inplace=True)
        if data.empty:
            raise ValueError(
                "The dataset is empty after dropping duplicates. Please adjust the 'drop_duplicates' parameter.")
    elif drop_duplicates:
        raise ParameterError('drop_duplicates', drop_duplicates, drop_duplicates_values)

    # Convert data types and process categorical values on demand
    datetime_columns: str = params.get("datetime_columns")
    if datetime_columns:
        try:
            dt_columns_decoded: Any = json.loads(datetime_columns)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error occurred when decoding provided JSON: \"{e}\"")

        if isinstance(dt_columns_decoded, str):
            dt_columns_decoded: list = [dt_columns_decoded]
        try:
            for col in dt_columns_decoded:
                if not isinstance(col, str):
                    raise TypeError
                try:
                    data[col] = pd.to_datetime(data[col])
                except KeyError:
                    raise ValueError(f"Column '{col}' to convert to datetime is not found in the DataFrame.")
                except ValueError:
                    raise ValueError(f"Column '{col}' could not be converted to datetime. Ensure the column contains "
                                     f"valid date/time values.")
        except TypeError:
            raise ParameterError("datetime_columns", datetime_columns, ["string", "array[string]"])

    category_columns = params.get("category_columns")
    if category_columns:
        try:
            cat_columns_decoded: Any = json.loads(category_columns)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error occurred when decoding provided JSON: \"{e}\"")

        if isinstance(cat_columns_decoded, str):
            cat_columns_decoded: list = [cat_columns_decoded]
        try:
            for col in cat_columns_decoded:
                if not isinstance(col, str):
                    raise TypeError
                try:
                    data[col] = data[col].astype('category')
                except KeyError:
                    raise ValueError(f"Column '{col}' to convert to category is not found in the DataFrame.")
                except ValueError:
                    raise ValueError(f"Column '{col}' could not be converted to category. Ensure the column contains "
                                     f"valid categorical values or check for unexpected data types.")
        except TypeError:
            raise ParameterError("category_columns", category_columns, ["string", "array[string]"])

    # Join small categories into one on demand
    def combine_rare_categories(df: pd.DataFrame, category_name: str, category_threshold: float) -> None:
        if not category_name:
            category_name = "Other"
        for col_name in df.select_dtypes(include='category').columns:
            category_counts = df[col_name].value_counts(normalize=True)
            if not category_threshold:
                category_threshold = category_counts.quantile(0.2)
            rare_categories = category_counts[category_counts <= category_threshold].index
            df[col_name] = df[col_name].apply(lambda x: category_name if x in rare_categories else x)

    join_small_cat: str = params.get('join_small_cat')
    if join_small_cat in join_small_cat_values:
        combine_rare_categories(data, params.get("joined_category_name"),
                                validate_positive_float_threshold("categories_threshold", params, 1))
    elif join_small_cat:
        raise ParameterError('join_small_cat', join_small_cat, join_small_cat_values)

    # Scale numeric data on demand
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

    scale_numeric: str = params.get("scale_numeric")
    if scale_numeric in scale_numeric_values:
        scale_numeric_data(data, params.get("scaling_method"))
    elif scale_numeric:
        raise ParameterError('scale_numeric', scale_numeric, scale_numeric_values)

    return data
# todo 4: for parameters where columns are listed add option to include all columns with *
# todo 3: refactor code
