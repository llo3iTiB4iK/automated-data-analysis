from pydantic import BaseModel, Field
from config import Config


class DatasetTokenHeader(BaseModel):
    x_dataset_token: str = Field(..., alias=Config.ACCESS_KEY_HEADER, description="Dataset access key")
