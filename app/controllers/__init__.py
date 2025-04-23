from typing import BinaryIO

import pandas as pd
import seaborn as sns
from werkzeug.datastructures import FileStorage

from app.models import LoadingParams, PreprocessingParams, AnalysisParams
from .dataframe_loader import DataFrameLoader
from .dataframe_preprocessor import DataFramePreprocessor
from .dataframe_report import DataFrameReport
from .recommender import Recommender

__all__ = ["load_data", "process_data", "get_data_report"]

sns.set_style("darkgrid")


def load_data(file: FileStorage, params: dict[str, str]) -> pd.DataFrame:
    model = LoadingParams(**params)
    loader = DataFrameLoader(file, model)
    return loader.load_data()


def process_data(data: pd.DataFrame, raw_params: dict[str, str]) -> pd.DataFrame:
    params = PreprocessingParams(**raw_params)
    preprocessor = DataFramePreprocessor(data)
    return preprocessor.preprocess_data(params)


def get_data_report(data: pd.DataFrame, raw_params: dict[str, str]) -> BinaryIO:
    report = DataFrameReport()

    report.add_heading(text="Overall dataset summary:")
    summary_text = f"* Data has {len(data)} rows and {len(data.columns)} columns:\n" \
                   f"    - {len(data.select_dtypes(include='number').columns)} numerical columns\n" \
                   f"    - {len(data.select_dtypes(include='category').columns)} categorical columns\n" \
                   f"    - {len(data.select_dtypes(include='bool').columns)} boolean columns\n" \
                   f"    - {len(data.select_dtypes(include='datetime').columns)} datetime columns\n" \
                   f"    - {len(data.select_dtypes(include='object').columns)} string columns.\n" \
                   f"* Duplicate rows were{'' if data.duplicated().any() else ' not'} found.\n" \
                   f"* Missing values share = {round(data.isna().values.sum() / data.size * 100, 2)}% ."
    report.add_text(text=summary_text)

    report.add_series(s=data.dtypes, title="Column Types:")

    if data.isna().values.any():
        counts_df = pd.DataFrame({
            'Missing values': data.isna().sum(),
            'Non-missing values': data.notna().sum()
        })
        counts_df.plot(kind='barh', stacked=True, title="Missing values by column")
        report.add_plot()

    report.add_dataframe(df=data.describe(exclude=['object', 'category', 'bool']), title="Numerical Data Stats:")
    report.add_dataframe(df=data.describe(include=['object', 'category', 'bool']), title="Non-Numerical Data Stats:")

    recs = Recommender(data, report)
    recs.make_recommendations(AnalysisParams(**raw_params))

    return report.to_bytes()
