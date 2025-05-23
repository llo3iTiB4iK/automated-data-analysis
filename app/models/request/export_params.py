from dataclasses import dataclass

import pandas as pd
from pydantic import BaseModel, constr, field_validator

from app.errors import ParameterError


@dataclass(frozen=True)
class ExportFormat:
    mimetype: str
    ext: str
    method: callable


EXPORT_FORMATS: dict[str, ExportFormat] = {
    "csv": ExportFormat("text/csv", "csv", pd.DataFrame.to_csv),
    "json": ExportFormat("application/json", "json", pd.DataFrame.to_json),
    "excel": ExportFormat("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "xlsx", pd.DataFrame.to_excel),
    "pickle": ExportFormat("application/octet-stream", "pkl", pd.DataFrame.to_pickle)
}


class ExportParams(BaseModel):
    format: constr(to_lower=True) = "csv"

    @field_validator("format")  # noqa
    @classmethod
    def validate_format(cls, v: str) -> str:
        if v not in EXPORT_FORMATS:
            raise ParameterError("format", v, list(EXPORT_FORMATS.keys()))
        return v

    @property
    def mimetype(self) -> str:
        return EXPORT_FORMATS[self.format].mimetype

    @property
    def ext(self) -> str:
        return EXPORT_FORMATS[self.format].ext

    @property
    def method(self) -> callable:
        return EXPORT_FORMATS[self.format].method
