from .base_error import BaseError


class EmptyDataset(BaseError):

    def __init__(self, context: str):
        self.context = context

    def to_dict(self) -> dict[str, str]:
        error = {
            "error": "Empty dataset",
            "message": self.context,
        }
        return error
