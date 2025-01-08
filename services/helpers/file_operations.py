import pandas as pd
import sqlite3
import tempfile
import os
from werkzeug.datastructures.file_storage import FileStorage
from errors import ParameterError


def create_temp_file(file_content: str | bytes, file_format: str = None) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_format) as temp_file:
        temp_file.write(file_content)
        return temp_file.name


def extract_kwargs(params: dict, keys: list) -> dict:
    return {key: params[key] for key in keys if key in params and params[key]}


def load_csv(file: FileStorage, params: dict) -> pd.DataFrame:
    kwargs = extract_kwargs(params, ["sep", "thousands", "decimal"])
    return pd.read_csv(file.stream, **kwargs)


def load_excel(file: FileStorage, params: dict) -> pd.DataFrame:
    kwargs = extract_kwargs(params, ["sheet_name", "thousands", "decimal"])
    return pd.read_excel(file.stream.read(), **kwargs)


def load_json(file: FileStorage, _: dict) -> pd.DataFrame:
    return pd.read_json(file.stream)


def load_sqlite(file: FileStorage, params: dict) -> pd.DataFrame:
    table_name: str = params['table_name']
    temp_file_path = create_temp_file(file.read(), ".db")

    cnx: sqlite3.Connection = sqlite3.connect(temp_file_path)
    try:
        return pd.read_sql(f"SELECT * FROM {table_name}", cnx)
    except pd.errors.DatabaseError:
        cursor: sqlite3.Cursor = cnx.execute("SELECT name FROM sqlite_master WHERE type='table';")
        existing_tables: list = [record[0] for record in cursor.fetchall()]
        raise ParameterError('table_name', table_name, existing_tables)
    finally:
        cnx.close()
        os.remove(temp_file_path)


def load_data(file: FileStorage, extension: str, params: dict) -> pd.DataFrame:
    loaders: dict = {
        'csv': load_csv,
        'xls': load_excel,
        'xlsx': load_excel,
        'json': load_json,
        'db': load_sqlite
    }

    if extension not in loaders:
        raise ValueError(f"Unsupported file format: '{extension}'. Supported formats: {', '.join(loaders.keys())}")

    return loaders[extension](file, params)
