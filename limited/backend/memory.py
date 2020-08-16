from threading import Lock
from time import monotonic
from typing import MutableMapping, NamedTuple

from limited.rate import Rate

from .interface import Backend, ZoneBackend

try:
    from cachetools import TTLCache  # type: ignore
except ImportError:
    raise ImportError('Must have cachetools installed to use memory backend.')


class Bucket(NamedTuple):
    tokens: float
    last_updated: float


class MemoryBackend(Backend):
    def __call__(self, name: str, rate: Rate) -> ZoneBackend:
        cache = TTLCache(None, rate.time)
        return MemoryZoneBackend(cache, rate)

    @classmethod
    def from_env(cls, environ) -> 'MemoryBackend':
        pass

    @classmethod
    def from_ini(cls, settings) -> 'MemoryBackend':
        pass


class MemoryZoneBackend(ZoneBackend):
    lock: Lock

    def __init__(self, mapping: MutableMapping[str, Bucket], rate: Rate):
        self.lock = Lock()
        self.mapping = mapping
        self.rate = rate
        self.size = rate.count

    def _count(self, key: str, time: float) -> float:
        bucket = self.mapping.get(key)
        if bucket is None:
            return self.size
        delta = time - bucket.last_updated
        tokens = bucket.tokens + delta * (self.rate.count / self.rate.time)
        tokens = min(tokens, self.size)
        return tokens

    def count(self, key: str) -> float:
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
