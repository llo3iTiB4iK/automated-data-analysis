from typing import Optional

from .info_response import InfoResponse


class PreprocessingResponse(InfoResponse):
    new_dataset_id: Optional[str] = None
    new_dataset_access_key: Optional[str] = None
