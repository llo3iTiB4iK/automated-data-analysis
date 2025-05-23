from .info_response import InfoResponse


class UploadResponse(InfoResponse):
    access_key: str
