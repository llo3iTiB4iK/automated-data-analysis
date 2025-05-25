from enum import Enum
from typing import Optional

from pydantic import BaseModel, field_validator, model_validator, PositiveInt
from typing_extensions import Self

from app.errors import ParameterMissing


class AnalysisTask(str, Enum):
    REGRESSION = "regression"
    CLASSIFICATION = "classification"
    CLUSTERIZATION = "clusterization"


class DocumentTheme(str, Enum):
    LIGHT = "light"
    DARK = "dark"


class AnalysisParams(BaseModel):
    analysis_task: AnalysisTask
    target_col: Optional[str] = None
    include_basic_stats: bool = True
    include_visualizations: bool = True
    dpi: PositiveInt = 200
    theme: DocumentTheme = DocumentTheme.LIGHT
    show_time: bool = True

    @field_validator("analysis_task", mode='before')  # noqa
    @classmethod
    def normalize_analysis_task(cls, v: str) -> str:
        return v.lower()

    @field_validator("theme", mode='before')  # noqa
    @classmethod
    def normalize_theme(cls, v: str) -> str:
        return v.lower()

    @model_validator(mode='after')
    def validate_target_column(self) -> Self:
        if self.analysis_task == AnalysisTask.CLUSTERIZATION and self.target_col is None:
            self.target_col = "Cluster"
        elif self.target_col is None:
            raise ParameterMissing("target_col")
        return self
