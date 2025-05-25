import os
import sqlite3
import tempfile
from io import BytesIO

import pandas as pd
from werkzeug.datastructures.file_storage import FileStorage

from app.errors import EmptyDataset, ReadingError
from app.models import LoadingParams


class DataFrameLoader:

    def __init__(self, file: FileStorage, params: LoadingParams) -> None:
        self.file = file
        self.params = params

    def __error(self, desc: str) -> ReadingError:
        raise ReadingError(self.file.filename, desc)

    def _load_csv(self) -> pd.DataFrame:
        return pd.read_csv(self.file.stream, sep=self.params.separator, thousands=self.params.thousands,
                           decimal=self.params.decimal)

    def _load_excel(self) -> pd.DataFrame:
        sheet_name = self.params.sheet_name
        xls = pd.ExcelFile(BytesIO(self.file.stream.read()))
        available = xls.sheet_names
        if isinstance(sheet_name, str) and sheet_name not in available:
            raise self.__error(f"Sheet '{sheet_name}' not found in Excel file. Available sheets: {available}")

        return xls.parse(sheet_name=sheet_name, thousands=self.params.thousands, decimal=self.params.decimal)

    def _load_json(self) -> pd.DataFrame:
        return pd.read_json(self.file.stream)

    def _load_sqlite(self) -> pd.DataFrame:
        table_name = self.params.table_name

        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as temp_file:
            temp_file.write(self.file.read())
            temp_file_path = temp_file.name

        cnx = sqlite3.connect(temp_file_path)
        try:
            return pd.read_sql(f"SELECT * FROM {table_name}", cnx)
        except pd.errors.DatabaseError:
            cursor = cnx.execute("SELECT name FROM sqlite_master WHERE type='table';")
            available = [record[0] for record in cursor.fetchall()]
            raise self.__error(f"Table '{table_name}' not found in the SQLite file. Available tables: {available}'")
        finally:
            cnx.close()
            os.remove(temp_file_path)

    def load_data(self) -> pd.DataFrame:
        LOADERS = {
            'csv': self._load_csv,
            'xls': self._load_excel,
            'xlsx': self._load_excel,
            'json': self._load_json,
            'db': self._load_sqlite
        }

        extension = self.file.filename.split('.')[-1].lower()

        if extension not in LOADERS:
            raise self.__error(f"Unsupported file extension '{extension}'. Supported types: {list(LOADERS.keys())}")

        try:
            data = LOADERS[extension]()
        except ReadingError:
            raise
        except Exception:
            raise self.__error("The data may be corrupted or incorrectly formatted. "
                               "Please check the file and try again later.")

        if data.empty:
            raise EmptyDataset(f"The uploaded file '{self.file.filename}' contains no data")

        return data
