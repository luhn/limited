from typing import NoReturn, Tuple

from .backend.interface import ZoneBackend


class Zone:
    def __init__(
            self,
            name: str,
            backend: ZoneBackend,
    ):
        self.backend = backend

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


def parse_rate(s: str) -> Tuple[float, int]:
    return 1.0, 1
