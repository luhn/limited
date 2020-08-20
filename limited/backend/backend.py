from abc import ABC, abstractmethod

from .zone import Zone


class Backend(ABC):
    @abstractmethod
    def __call__(self, name: str, rate: float, size: int) -> Zone:
        """
        Create a new zone backend.

        """
        pass

    @classmethod
    @abstractmethod
    def from_env(cls, environ) -> 'Backend':
        """
        Configure backend from environment variables.

        """
        pass

    @classmethod
    @abstractmethod
    def from_ini(cls, settings) -> 'Backend':
        """
        Configure backend from ini file.

        """
        pass
