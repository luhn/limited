from abc import ABC, abstractmethod
from typing import NoReturn, Any, Mapping

from limited.exceptions import LimitExceededException


class Backend(ABC):
    SETTINGS: Mapping[str, type] = dict()

    # rate: float
    # size: int

    # @abstractmethod
    # def __init__(**settings: Mapping[str, Any]):
    #     ...

    @abstractmethod
    def count(self, zone: str, identity: str) -> int:
        """
        Return the number of tokens in the bucket.  Optionally may return
        partial tokens.

        """
        ...

    @abstractmethod
    def remove(self, zone: str, identity: str, count: int) -> bool:
        """
        Remove a number of tokens.  Return false if the bucket does not have
        sufficient tokens.

        """
        ...

    # @property
    # def ttl(self) -> float:
    #     return self.size / self.rate

    # def check(self, zone: str, identity: str) -> bool:
    #     return self.count(zone, identity) >= 1

    # def increment(self, zone: str, identity: str) -> None:
    #     self.remove(zone, identity, 1)

    # def limit(self, zone: str, identity: str) -> bool:
    #     """
    #     Return true if limit is hit.

    #     """
    #     return not self.remove(zone, identity, 1)

    # def hard_limit(self, zone: str, identity: str) -> None:
    #     if not self.remove(identity, 1):
    #         self._raise()

    # def _raise(self) -> NoReturn:
    #     raise LimitExceededException()
