from abc import ABC, abstractmethod
from typing import NoReturn

from limited.exceptions import LimitExceededException


class Zone(ABC):
    rate: float
    size: int

    @abstractmethod
    def count(self, identity: str) -> int:
        """
        Return the number of tokens in the bucket.  Optionally may return
        partial tokens.

        """
        pass

    @abstractmethod
    def remove(self, identity: str, count: int) -> bool:
        """
        Remove a number of tokens.  Return false if the bucket does not have
        sufficient tokens.

        """
        pass

    @property
    def ttl(self) -> float:
        return self.size / self.rate

    def check(self, identity: str) -> bool:
        return self.count(identity) >= 1

    def increment(self, identity: str) -> None:
        self.remove(identity, 1)

    def limit(self, identity: str) -> bool:
        """
        Return true if limit is hit.

        """
        return not self.remove(identity, 1)

    def hard_limit(self, identity: str) -> None:
        if not self.remove(identity, 1):
            self._raise()

    def _raise(self) -> NoReturn:
        raise LimitExceededException()
