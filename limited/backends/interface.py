from abc import ABC, abstractmethod


class Backend(ABC):
    @abstractmethod
    def count(self, key: str, size: int, rate: float) -> float:
        """
        Return the number of tokens in the bucket.  Optionally may return
        partial tokens.

        """
        pass

    @abstractmethod
    def remove(self, key: str, count: int, size: int, rate: float) -> bool:
        """
        Remove a number of tokens.  Return false if the bucket does not have
        sufficient tokens.

        """
        pass
