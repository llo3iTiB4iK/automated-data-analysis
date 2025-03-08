import pandas as pd
import sqlite3
import os
import tempfile
from io import BytesIO
from werkzeug.datastructures.file_storage import FileStorage
from errors import ParameterError


class DataFrameLoader:

    def __init__(self, file: FileStorage, params: dict):
        self.file: FileStorage = file
        self.params: dict = params

    def __extract_kwargs(self, keys: list) -> dict:
        return {key: self.params[key] for key in keys if key in self.params and self.params[key]}

    def _load_csv(self) -> pd.DataFrame:
        kwargs = self.__extract_kwargs(["sep", "thousands", "decimal"])
        return pd.read_csv(self.file.stream, **kwargs)

    def _load_excel(self) -> pd.DataFrame:
        kwargs = self.__extract_kwargs(["sheet_name", "thousands", "decimal"])
        return pd.read_excel(BytesIO(self.file.stream.read()), **kwargs)

    def _load_json(self) -> pd.DataFrame:
        return pd.read_json(self.file.stream)

    def _load_sqlite(self) -> pd.DataFrame:
        table_name: str = self.params['table_name']

        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as temp_file:
            temp_file.write(self.file.read())
            temp_file_path = temp_file.name

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

    def load_data(self) -> pd.DataFrame:
        loaders: dict = {
            'csv': self._load_csv,
            'xls': self._load_excel,
            'xlsx': self._load_excel,
            'json': self._load_json,
            'db': self._load_sqlite
        }

        extension: str = self.file.filename.split('.')[-1].lower()
        if extension not in loaders:
            raise ValueError(f"Unsupported file format: '{extension}'. Supported formats: {', '.join(loaders.keys())}")

        data: pd.DataFrame = loaders[extension]()
        if data.empty:
            raise ValueError("The uploaded file contains no data. Please upload a file with valid data.")

        return data
