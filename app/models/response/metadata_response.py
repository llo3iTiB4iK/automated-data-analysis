from pydantic import BaseModel


class MetadataResponse(BaseModel):
    num_rows: int
    num_columns: int
    columns: dict[str, str]
