from abc import ABC, abstractmethod


class BaseError(Exception, ABC):
    @abstractmethod
    def to_dict(self) -> dict:
        pass
