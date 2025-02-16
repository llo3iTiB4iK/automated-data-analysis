import pandas as pd
import sqlite3
import os
import tempfile
from werkzeug.datastructures.file_storage import FileStorage
from errors import ParameterError


class DataLoader:

    def __init__(self, file: FileStorage, params: dict):
        self.file: FileStorage = file
        self.params: dict = params

    def extract_kwargs(self, keys: list) -> dict:
        return {key: self.params[key] for key in keys if key in self.params and self.params[key]}

    def load_csv(self) -> pd.DataFrame:
        kwargs = self.extract_kwargs(["sep", "thousands", "decimal"])
        return pd.read_csv(self.file.stream, **kwargs)

    def load_excel(self) -> pd.DataFrame:
        kwargs = self.extract_kwargs(["sheet_name", "thousands", "decimal"])
        return pd.read_excel(self.file.stream.read(), **kwargs)

    def load_json(self) -> pd.DataFrame:
        return pd.read_json(self.file.stream)

    def load_sqlite(self) -> pd.DataFrame:
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
