from pydantic import BaseModel

from .metadata_response import MetadataResponse


class InfoResponse(BaseModel):
    message: str
    dataset_id: str
    next_step: str
    metadata: MetadataResponse
