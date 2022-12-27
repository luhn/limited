from threading import Lock
from time import monotonic
from typing import MutableMapping, NamedTuple, Mapping

from .backend import Backend

try:
    from cachetools import TTLCache  # type: ignore
except ImportError:
    raise ImportError('Must have cachetools installed to use memory backend.')


class Bucket(NamedTuple):
    tokens: float
    last_updated: float


class MemoryZone(Backend):
    SETTINGS = {
        'store_size': int,
    }

    lock: Lock
    mappings: MutableMapping[tuple[str, str], Bucket]

    def __init__(self, store_size: int):
        assert not settings
        self.mappings = TTLCache(store_size, self.ttl)
        self.lock = Lock()

    def _count(self, zone: str, key: str, time: float) -> int:
        bucket = self.mapping.get((zone, key))
        if bucket is None:
            return self.size
        delta = time - bucket.last_updated
        tokens = bucket.tokens + delta * self.rate
        tokens = min(tokens, self.size)
        return int(tokens)

    def count(self, zone: str, key: str) -> int:
        return self._count(zone, key, monotonic())

    def remove(self, zone: str, key: str, count: int) -> bool:
        with self.lock:
            now = monotonic()
            tokens = self._count(zone, key, now)
            if tokens < count:
                return False
            else:
                self.mapping[(zone, key)] = Bucket(tokens - count, now)
                return True
