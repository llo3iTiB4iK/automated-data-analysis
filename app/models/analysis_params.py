from typing import Optional, Literal

from pydantic import BaseModel


class AnalysisParams(BaseModel):
    analysis_task: Literal["regression", "classification", "clusterization"]
    target_col: Optional[str] = None
