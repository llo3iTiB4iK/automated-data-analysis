import pandas as pd
from werkzeug.datastructures.file_storage import FileStorage
from services.helpers.validators import ensure_not_empty
from services.helpers.dataframe_loader import DataLoader


def load_data(file: FileStorage, params: dict) -> pd.DataFrame:
    loader: DataLoader = DataLoader(file, params)
    loaders: dict = {
        'csv': loader.load_csv,
        'xls': loader.load_excel,
        'xlsx': loader.load_excel,
        'json': loader.load_json,
        'db': loader.load_sqlite
    }
    extension: str = file.filename.split('.')[-1].lower()
    if extension not in loaders:
        raise ValueError(f"Unsupported file format: '{extension}'. Supported formats: {', '.join(loaders.keys())}")

    data = loaders[extension]()
    ensure_not_empty(data, "The uploaded file contains no data. Please upload a file with valid data.")
    return data
