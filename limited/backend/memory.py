from threading import Lock
from time import monotonic
from typing import MutableMapping, NamedTuple

from .backend import Backend
from .zone import Zone

try:
    from cachetools import TTLCache  # type: ignore
except ImportError:
    raise ImportError('Must have cachetools installed to use memory backend.')


class Bucket(NamedTuple):
    tokens: float
    last_updated: float


class MemoryBackend(Backend):
    def __init__(self, size: int):
        self.size = size

    def __call__(self, name: str, rate: float, size: int) -> Zone:
        return MemoryZone(self.size, rate, size)

    @classmethod
    def from_env(cls, environ) -> 'MemoryBackend':
        pass

    @classmethod
    def from_ini(cls, settings) -> 'MemoryBackend':
        pass


class MemoryZone(Zone):
    lock: Lock
    mapping: MutableMapping[str, Bucket]

    def __init__(self, store_size: int, rate: float, bucket_size: int):
        self.rate = rate
        self.size = bucket_size
        self.mapping = TTLCache(store_size, self.ttl)
        self.lock = Lock()

    def _count(self, key: str, time: float) -> int:
        bucket = self.mapping.get(key)
        if bucket is None:
            return self.size
        delta = time - bucket.last_updated
        tokens = bucket.tokens + delta * self.rate
        tokens = min(tokens, self.size)
        return int(tokens)

    def count(self, key: str) -> int:
        return self._count(key, monotonic())

    def remove(self, key: str, count: int) -> bool:
        with self.lock:
            now = monotonic()
            tokens = self._count(key, now)
            if tokens < count:
                return False
            else:
                self.mapping[key] = Bucket(tokens - count, now)
                return True
