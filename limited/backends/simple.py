from time import monotonic
from threading import Lock
from typing import Dict, NamedTuple
from .interface import Backend


class Bucket(NamedTuple):
    tokens: float
    last_updated: float


class SimpleBackend(Dict[str, Bucket], Backend):
    lock: Lock

    def __init__(self):
        dict.__init__(self)
        self.lock = Lock()

    def _refill(self, bucket: Bucket, size: float, rate: float) -> Bucket:
        time = monotonic()
        delta = time - bucket.last_updated
        tokens = bucket.tokens + delta * rate
        tokens = max(min(tokens, size), 0.0)
        return Bucket(tokens, time)

    def _get_bucket(self, key: str, size: float, rate: float):
        bucket = self.pop(key, None)
        if bucket is None:
            return Bucket(size, monotonic())
        else:
            return self._refill(bucket, size, rate)

    def count(self, key: str, size: int, rate: float) -> float:
        size = float(size)
        with self.lock:
            bucket = self._get_bucket(key, size, rate)
            if bucket.tokens == size:
                return size  # Bucket is full, don't persist it
            else:
                self[key] = bucket  # Persist bucket
                return bucket.tokens

    def remove(self, key: str, count: int, size: int, rate: float) -> bool:
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
