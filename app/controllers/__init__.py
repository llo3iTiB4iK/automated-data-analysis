from typing import BinaryIO

import pandas as pd
from werkzeug.datastructures import FileStorage

from app.models import LoadingParams, PreprocessingParams, AnalysisParams
from .dataframe_analyzer import DataFrameAnalyzer
from .dataframe_loader import DataFrameLoader
from .dataframe_preprocessor import DataFramePreprocessor
from .dataframe_report import DataFrameReport

__all__ = ["load_data", "process_data", "get_data_report"]


def load_data(file: FileStorage, raw_params: dict[str, str]) -> pd.DataFrame:
    params = LoadingParams(**raw_params)
    loader = DataFrameLoader(file, params)
    return loader.load_data()


def process_data(data: pd.DataFrame, raw_params: dict[str, str]) -> pd.DataFrame:
    preprocessor = DataFramePreprocessor(data)
    params = PreprocessingParams(**raw_params)
    return preprocessor.preprocess_data(params)


def get_data_report(data: pd.DataFrame, raw_params: dict[str, str]) -> BinaryIO:
    report = DataFrameReport()
    analyzer = DataFrameAnalyzer(data, report)
    params = AnalysisParams(**raw_params)
    analyzer.generate_report(params)
    return report.to_bytes()
