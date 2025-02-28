import pandas as pd
from typing import Any
from errors import ParameterError
from services.helpers.dataframe_report import DataFrameReport


class Recommender:

    def __init__(self, data: pd.DataFrame, report: DataFrameReport):
        self.data: pd.DataFrame = data
        self.report: DataFrameReport = report
        self.target_col: Any = None

    def __validate_target_col(self) -> None:  # TODO: review necessity of this method
        if self.target_col not in self.data.columns:
            raise ValueError(f"Target column '{self.target_col}' not found in the DataFrame.")

    def _regression_recommendations(self) -> None:
        self.__validate_target_col()
        # TODO: make recommendations

    def _classification_recommendations(self) -> None:
        self.__validate_target_col()
        # TODO: make recommendations

    def _clusterization_recommendations(self) -> None:
        if not self.target_col:
            self.target_col = "Cluster"
        # TODO: make recommendations

    def make_recommendations(self, analysis_task: str, target_col: str) -> None:
        self.target_col = target_col
        recommenders: dict = {
            'regression': self._regression_recommendations,
            'classification': self._classification_recommendations,
            'clusterization': self._clusterization_recommendations
        }

        if analysis_task not in recommenders:
            raise ParameterError("analysis_task", analysis_task, list(recommenders.keys()))

        return recommenders[analysis_task]
