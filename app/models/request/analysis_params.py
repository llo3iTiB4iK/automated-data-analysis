from enum import Enum
from typing import Optional

from pydantic import BaseModel, field_validator, model_validator
from typing_extensions import Self


class AnalysisTask(str, Enum):
    REGRESSION = "regression"
    CLASSIFICATION = "classification"
    CLUSTERIZATION = "clusterization"


class AnalysisParams(BaseModel):
    analysis_task: AnalysisTask
    target_col: Optional[str] = None

    @field_validator("analysis_task", mode='before')  # noqa
    @classmethod
    def normalize_analysis_task(cls, v: str) -> str:
        return v.lower()

    @model_validator(mode='after')
    def set_clustering_target(self) -> Self:
        if self.analysis_task == AnalysisTask.CLUSTERIZATION and self.target_col is None:
            self.target_col = "Cluster"
        return self
