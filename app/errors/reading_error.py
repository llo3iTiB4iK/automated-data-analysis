from .base_error import BaseError


class ReadingError(BaseError):

    def __init__(self, message: str, filename: str) -> None:
        self.message = message
        self.file = filename

    def to_dict(self) -> dict[str, str]:
        return {
            "error": "Reading error",
            "file": self.file,
            "details": self.message
        }
