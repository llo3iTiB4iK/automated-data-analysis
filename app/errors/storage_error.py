from .base_error import BaseError


class StorageError(BaseError):

    def __init__(self, message: str, status: int = None) -> None:
        self.message = message
        self.status = status or self.status

    def to_dict(self) -> dict[str, str]:
        return {
            "error": "Storage error",
            "message": self.message
        }
