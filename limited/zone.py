from typing import NoReturn, Union

from .backend.interface import Backend, ZoneBackend
from .rate import Rate, parse_rate


class Zone:
    backend: ZoneBackend

    def __init__(
            self,
            name: str,
            rate: Union[Rate, str],
            backend: Backend,
    ):
        if isinstance(rate, str):
            rate = parse_rate(rate)
        self.backend = backend(name, rate)

    def get(self, identity: str) -> int:
        return int(self.backend.count(identity))

    def check(self, identity: str) -> bool:
        return self.get(identity) >= 1

    def increment(self, identity: str) -> None:
        self.backend.remove(identity, 1)

    def limit(self, identity: str) -> bool:
        return not self.backend.remove(identity, 1)

    def hard_limit(self, identity: str) -> None:
        if self.limit(identity):
            self._raise()

    def _raise(self) -> NoReturn:
        raise LimitExceededException()


class LimitExceededException(Exception):
    pass
