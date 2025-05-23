from typing import Optional

from pydantic import BaseModel, Field


class LoadingParams(BaseModel):
    sep: Optional[str] = None
    thousands: Optional[str] = Field(None, min_length=1, max_length=1)
    decimal: Optional[str] = Field(None, min_length=1, max_length=1)
    sheet_name: Optional[str] = None
    table_name: Optional[str] = None

    def get_kwargs(self, *args) -> dict:
        return self.dict(include=set(args), exclude_none=True)
