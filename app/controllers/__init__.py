from typing import BinaryIO

import pandas as pd
from werkzeug.datastructures import FileStorage

from app.models import LoadingParams, PreprocessingParams, AnalysisParams
from .dataframe_analyzer import DataFrameAnalyzer
from .dataframe_loader import DataFrameLoader
from .dataframe_preprocessor import DataFramePreprocessor

__all__ = ["load_data", "process_data", "get_data_report"]


def load_data(file: FileStorage, raw_params: dict[str, str]) -> pd.DataFrame:
    params = LoadingParams(**raw_params)
    loader = DataFrameLoader(file, params)
    return loader.load_data()


def process_data(data: pd.DataFrame, raw_params: dict[str, str]) -> pd.DataFrame:
    preprocessor = DataFramePreprocessor(data)
    params = PreprocessingParams(**raw_params)
    return preprocessor.preprocess(params)


def get_data_report(data: pd.DataFrame, raw_params: dict[str, str]) -> BinaryIO:
    analyzer = DataFrameAnalyzer(data)
    params = AnalysisParams(**raw_params)
    report = analyzer.fill_report(params)
    return report.to_bytes()
