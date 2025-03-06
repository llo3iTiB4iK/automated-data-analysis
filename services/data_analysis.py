import pandas as pd
import seaborn as sns
from typing import BinaryIO
from services.helpers.dataframe_report import DataFrameReport
from services.helpers.recommender import Recommender

sns.set_style("darkgrid")


def get_data_report(data: pd.DataFrame, params: dict) -> BinaryIO:
    report: DataFrameReport = DataFrameReport()

    report.add_heading(text="Overall dataset summary:")
    summary_text: str = f"* Data has {len(data)} rows and {len(data.columns)} columns:\n" \
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
        counts_df: pd.DataFrame = pd.DataFrame({
            'Missing values': data.isna().sum(),
            'Non-missing values': data.notna().sum()
        })
        counts_df.plot(kind='barh', stacked=True, title="Missing values by column")
        report.add_plot()

    report.add_dataframe(df=data.describe(exclude=['object', 'category', 'bool']), title="Numerical Data Stats:")
    report.add_dataframe(df=data.describe(include=['object', 'category', 'bool']), title="Non-Numerical Data Stats:")

    recommender: Recommender = Recommender(data, report)
    recommender.make_recommendations(
        analysis_task=params["analysis_task"],
        target_col=params.get("target_col")
    )

    return report.to_bytes()
