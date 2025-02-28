import pandas as pd
from werkzeug.datastructures.file_storage import FileStorage
from services.helpers.dataframe_loader import DataFrameLoader


def load_data(file: FileStorage, params: dict) -> pd.DataFrame:
    loader: DataFrameLoader = DataFrameLoader(file, params)
    return loader.load_data()
