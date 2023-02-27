from threading import Lock
from time import monotonic
from typing import MutableMapping, NamedTuple

from ..zone import Zone
from .backend import Backend

try:
    from cachetools import LRUCache  # type: ignore
except ImportError:
    raise ImportError('Must have cachetools installed to use memory backend.')


class Bucket(NamedTuple):
    tokens: float
    last_updated: float


class MemoryBackend(Backend):
    SETTINGS = {
        'store_size': int,
    }

    lock: Lock
    buckets: MutableMapping[tuple[str, str], Bucket]

    def __init__(self, store_size: int):
        self.buckets = LRUCache(store_size)
        self.lock = Lock()

    def _count(self, zone: Zone, key: str, time: float) -> int:
        bucket = self.buckets.get((zone.name, key))
        if bucket is None:
            return zone.rate.count
        delta = time - bucket.last_updated
        tokens = bucket.tokens + delta * zone.rate
        tokens = min(tokens, zone.rate.count)
        return int(tokens)

    def count(self, zone: Zone, key: str) -> int:
        return self._count(zone, key, monotonic())

    def remove(self, zone: Zone, key: str, count: int) -> bool:
        with self.lock:
            now = monotonic()
            tokens = self._count(zone, key, now)
            if tokens < count:
                return False
            else:
                self.buckets[(zone.name, key)] = Bucket(tokens - count, now)
                return True
