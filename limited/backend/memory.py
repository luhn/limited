from threading import Lock
from time import monotonic
from typing import MutableMapping, NamedTuple

from limited.rate import Rate

from .interface import Backend, ZoneBackend

try:
    from cachetools import TTLCache  # type: ignore
except ImportError:
    TTLCache = None


class Bucket(NamedTuple):
    tokens: float
    last_updated: float


class MemoryBackend(Backend):
    def __init__(self):
        if TTLCache is None:
            raise ImportError(
                'Must have cachetools installed to use memory backend.'
            )

    def __call__(self, name: str, rate: Rate) -> ZoneBackend:
        cache = TTLCache(None, rate.time)
        return MemoryZoneBackend(cache, rate)


class SimpleMemoryBackend(Backend):
    def __call__(self, name: str, rate: Rate) -> ZoneBackend:
        return MemoryZoneBackend(dict(), rate)


class MemoryZoneBackend(ZoneBackend):
    lock: Lock
    mapping: MutableMapping

    def __init__(self, mapping: MutableMapping, rate: Rate):
        self.lock = Lock()
        self.mapping = mapping
        self.rate = rate
        self.size = rate.count

    def _refill(self, bucket: Bucket) -> Bucket:
        time = monotonic()
        delta = time - bucket.last_updated
        tokens = bucket.tokens + delta * (self.rate.count / self.rate.time)
        tokens = max(min(tokens, self.size), 0.0)
        return Bucket(tokens, time)

    def _get_bucket(self, key: str):
        bucket = self.mapping.pop(key, None)
        if bucket is None:
            return Bucket(self.size, monotonic())
        else:
            return self._refill(bucket)

    def count(self, key: str) -> float:
        with self.lock:
            bucket = self._get_bucket(key)
            if bucket.tokens == self.size:
                return float(self.size)  # Bucket is full, don't persist it
            else:
                self.mapping[key] = bucket  # Persist bucket
                return bucket.tokens

    def remove(self, key: str, count: int) -> bool:
        with self.lock:
            bucket = self._get_bucket(key)
            if bucket.tokens < count:
                # Not enough tokens
                self.mapping[key] = bucket
                return False
            else:
                tokens = bucket.tokens - count
                self.mapping[key] = Bucket(tokens, bucket.last_updated)
                return True
