from abc import ABC, abstractmethod

from limited import zone
from limited.rate import Rate


class Backend(ABC):
    @abstractmethod
    def __call__(self, name: str, rate: Rate) -> 'zone.ZoneBackend':
        """
        Create a new zone backend.

        """
        pass

    @classmethod
    @abstractmethod
    def from_env(cls, environ):
        """
        Configure backend from environment variables.

        """
        pass

    @classmethod
    @abstractmethod
    def from_ini(cls, settings):
        """
        Configure backend from ini file.

        """
        pass


class ZoneBackend(ABC):
    @abstractmethod
    def count(self, key: str) -> float:
        """
        Return the number of tokens in the bucket.  Optionally may return
        partial tokens.

        """
        pass

    @abstractmethod
    def remove(self, key: str, count: int) -> bool:
        """
        Remove a number of tokens.  Return false if the bucket does not have
        sufficient tokens.

        """
        pass
