from unittest.mock import Mock

import pytest

from limited.backend.memory import Bucket, MemoryBackend, MemoryZone


@pytest.fixture
def patch_time(monkeypatch):
    def patch_time(time):
        mock = Mock(return_value=time)
        monkeypatch.setattr('limited.backend.memory.monotonic', mock)

    return patch_time


def test_memory_backend():
    backend = MemoryBackend(100)
    zone = backend('test', 1.0, 10)
    assert isinstance(zone, MemoryZone)
    assert zone.rate == 1.0
    assert zone.size == 10


def test_memory_zone_count_not_set():
    "Test count when key doesn't exist."
    zone = MemoryZone(10, 1.0, 10)
    assert zone.count('a') == 10.0


def test_memory_zone_count(patch_time):
    zone = MemoryZone(10, 1.0, 10)
    zone.mapping['a'] = Bucket(1.0, 0.0)

    patch_time(0.0)
    assert zone.count('a') == 1.0
    patch_time(1.0)
    assert zone.count('a') == 2.0
    patch_time(20.0)
    assert zone.count('a') == 10.0


def test_memory_zone_remove(patch_time):
    zone = MemoryZone(10, 1.0, 10)
    zone.mapping['a'] = Bucket(1.0, 0.0)
    patch_time(2.0)
    assert zone.remove('a', 1)
    assert zone.mapping['a'] == Bucket(2.0, 2.0)  # Less one, plus two


def test_memory_zone_remove_empty(patch_time):
    zone = MemoryZone(10, 1.0, 10)
    patch_time(2.0)
    assert zone.remove('a', 1)
    assert zone.mapping['a'] == Bucket(9.0, 2.0)


def test_memory_zone_remove_insufficient(patch_time):
    zone = MemoryZone(10, 1.0, 10)
    zone.mapping['a'] = Bucket(0.0, 0.0)
    patch_time(0.0)
    assert not zone.remove('a', 1)
    assert zone.mapping['a'] == Bucket(0.0, 0.0)
