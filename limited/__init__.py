from .backends import Backend


Identity = Any


@dataclass(frozen=True)
class Rate:
    count: int
    time: float


class LimitedRegion:
    def __init__(self, backend):
        pass


class LimitExceededException(Exception):
    pass


class Zone:
    name: str
    backend: Backend
    size: int
    rate: int
    keyfunc: Callable[[str], str]

    def __init__(self, name: str, backend: Backend, rate: Rate, keyfunc: Callable[[str], str] = str):
        self.name = name
        self.backend = backend
        self.keyfunc = keyfunc

    def _key(self, identity: Identity):
        return self.name + ':' + self.keyfunc(str(identity))

    def get(self, identity: Any):
        key = self._key(identity)

    def check(self, identity: Any) -> bool:
        return self.backend.count() >= 1

    def increment(self, identity):
        key = self._key(identity)
        self.backend.remove(key, )

    def limit(self, identity) -> bool:
        return not self.backend.remove(request, identity)

    def hard_limit(self, identity) -> None:
        if self.limit():
            self._raise()

    def _raise(self) -> None:
        raise LimitExceededException()
