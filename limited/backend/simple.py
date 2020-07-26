from time import monotonic
from threading import Lock
from typing import Dict, NamedTuple
from .interface import Backend, ZoneBackend

try:
    from cachetools import TTLCache
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

    def _refill(self, bucket: Bucket) -> Bucket:
        time = monotonic()
        delta = time - bucket.last_updated
        tokens = bucket.tokens + delta * rate
        tokens = max(min(tokens, size), 0.0)
        return Bucket(tokens, time)

    def _get_bucket(self, key: str):
        bucket = self.pop(key, None)
        if bucket is None:
            return Bucket(size, monotonic())
        else:
            return self._refill(bucket, size, rate)

    def count(self, key: str) -> float:
        size = float(size)
        with self.lock:
            bucket = self._get_bucket(key, size, rate)
            if bucket.tokens == size:
                return size  # Bucket is full, don't persist it
            else:
                self[key] = bucket  # Persist bucket
                return bucket.tokens

    def remove(self, key: str, count: int) -> bool:
        size = float(size)
        with self.lock:
            bucket = self._get_bucket(key, size, rate)
            if bucket.tokens < count:
                # Not enough tokens
                self[key] = bucket
                return False
            else:
                tokens = bucket.tokens - count
                self[key] = Bucket(tokens, bucket.last_updated)
                return True
