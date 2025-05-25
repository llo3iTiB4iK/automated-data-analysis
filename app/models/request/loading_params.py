from typing import Optional

from pydantic import BaseModel, Field


class LoadingParams(BaseModel):
    separator: Optional[str] = ","
    thousands: Optional[str] = Field(None, min_length=1, max_length=1)
    decimal: Optional[str] = Field(".", min_length=1, max_length=1)
    sheet_name: Optional[str | int] = 0
    table_name: Optional[str] = None
