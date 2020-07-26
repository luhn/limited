from typing import Any, Union
from .backend.interface import ZoneBackend, Backend
from .rate import Rate


class Zone:
    name: str
    backend: ZoneBackend
    size: int
    rate: int

    def __init__(self, name: str, rate: Union[Rate, str], backend: Backend):
        if isinstance(rate, str):
            rate = parse_rate(s)
        self.backend = backend(name, rate)

    def get(self, identity: str) -> int:
        return self.backend.count(self._key(identity))

    def check(self, identity: str) -> bool:
        return self.get(identity) >= 1

    def increment(self, identity: str):
        self.backend.remove(self._key(identity))

    def limit(self, identity: str) -> bool:
        return not self.backend.remove(self._key(identity))

    def hard_limit(self, identity: str) -> None:
        if self.limit():
            self._raise()

    def _raise(self) -> None:
        raise LimitExceededException()


class LimitExceededException(Exception):
    pass
