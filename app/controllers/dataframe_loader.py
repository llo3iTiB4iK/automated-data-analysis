import os
import sqlite3
import tempfile
from io import BytesIO

import pandas as pd
from werkzeug.datastructures.file_storage import FileStorage

from app.errors import ParameterError, ParameterMissing, EmptyDataset, ReadingError
from app.models import LoadingParams


class DataFrameLoader:

    def __init__(self, file: FileStorage, params: LoadingParams) -> None:
        self.file = file
        self.params = params

    def _load_csv(self) -> pd.DataFrame:
        kwargs = self.params.get_kwargs("sep", "thousands", "decimal")
        return pd.read_csv(self.file.stream, **kwargs)

    def _load_excel(self) -> pd.DataFrame:
        kwargs = self.params.get_kwargs("sheet_name", "thousands", "decimal")
        sheet_name = kwargs.get("sheet_name")
        xls = pd.ExcelFile(BytesIO(self.file.stream.read()))
        existing_sheets = xls.sheet_names
        if sheet_name is not None and sheet_name not in existing_sheets:
            raise ParameterError("sheet_name", sheet_name, existing_sheets)

        return xls.parse(**kwargs)

    def _load_json(self) -> pd.DataFrame:
        return pd.read_json(self.file.stream)

    def _load_sqlite(self) -> pd.DataFrame:
        table_name = self.params.table_name
        if table_name is None:
            raise ParameterMissing("table_name")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as temp_file:
            temp_file.write(self.file.read())
            temp_file_path = temp_file.name

        cnx = sqlite3.connect(temp_file_path)
        try:
            return pd.read_sql(f"SELECT * FROM {table_name}", cnx)
        except pd.errors.DatabaseError:
            cursor = cnx.execute("SELECT name FROM sqlite_master WHERE type='table';")
            existing_tables = [record[0] for record in cursor.fetchall()]
            raise ParameterError('table_name', table_name, existing_tables)
        finally:
            cnx.close()
            os.remove(temp_file_path)

    def load_data(self) -> pd.DataFrame:
        loaders = {
            'csv': self._load_csv,
            'xls': self._load_excel,
            'xlsx': self._load_excel,
            'json': self._load_json,
            'db': self._load_sqlite
        }

        extension = self.file.filename.split('.')[-1].lower()

        if extension not in loaders:
            raise ParameterError("file", extension, list(loaders.keys()))

        try:
            data = loaders[extension]()
        except ValueError as e:
            raise ReadingError(e.args[0], self.file.filename)

        if data.empty:
            raise EmptyDataset(f"The uploaded file '{self.file.filename}' contains no data")

        return data
