from unittest.mock import Mock

import pytest

from limited.backend.memory import Bucket, MemoryBackend, MemoryZoneBackend
from limited.rate import Rate

RATE = Rate(count=10, time=10)


@pytest.fixture
def patch_time(monkeypatch):
    def patch_time(time):
        mock = Mock(return_value=time)
        monkeypatch.setattr('limited.backend.memory.monotonic', mock)

    return patch_time


def test_memory_backend():
    backend = MemoryBackend()
    zone = backend('test', RATE)
    assert isinstance(zone, MemoryZoneBackend)
    assert zone.rate == RATE
    assert zone.size == 10.0


def test_memory_zone_backend_count_not_set():
    "Test count when key doesn't exist."
    zone = MemoryZoneBackend(dict(), RATE)
    assert zone.count('a') == 10.0


def test_memory_zone_backend_count(patch_time):
    mapping = {
        'a': Bucket(1.0, 0.0),
    }
    zone = MemoryZoneBackend(mapping, RATE)

    patch_time(0.0)
    assert zone.count('a') == 1.0
    patch_time(1.0)
    assert zone.count('a') == 2.0
    patch_time(20.0)
    assert zone.count('a') == 10.0
