from abc import ABC, abstractmethod


class BaseError(Exception, ABC):
    status = 400

    @abstractmethod
    def to_dict(self) -> dict:
        pass
