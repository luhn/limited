from collections import defaultdict
from typing import MutableMapping

import pytest

from limited import LimitExceededException, Rate, Zone
from limited.backend.interface import Backend, ZoneBackend

Buckets = MutableMapping[str, float]


class MockBackend(Backend):
    def __call__(self, name: str, rate: Rate) -> ZoneBackend:
        return MockZoneBackend(name, rate)

    @classmethod
    def from_env(cls, environ) -> Backend:
        raise NotImplementedError()

    @classmethod
    def from_ini(cls, settings) -> Backend:
        raise NotImplementedError()


class MockZoneBackend(ZoneBackend):
    name: str
    rate: Rate
    buckets: Buckets

    def __init__(self, name: str, rate: Rate):
        self.name = name
        self.rate = rate
        self.buckets = defaultdict(lambda: float(rate.count))

    def count(self, key: str) -> float:
        return self.buckets[key]

    def remove(self, key: str, count: int) -> bool:
        if self.buckets[key] >= count:
            self.buckets[key] -= count
            return True
        else:
            return False


@pytest.fixture
def zone():
    return Zone('name', Rate(10, 5), MockBackend())


@pytest.fixture
def buckets(zone):
    return zone.backend.buckets


def test_zone_init():
    zone = Zone('name', Rate(4, 5), MockBackend())
    backend = zone.backend
    assert isinstance(backend, MockZoneBackend)
    assert backend.name == 'name'
    assert backend.rate == Rate(4, 5)


def test_zone_init_parse():
    """Test parsing rate string when initializing zone."""
    pass  # TODO


def test_zone_get(zone: Zone, buckets: Buckets):
    buckets['a'] = 5.5
    zone.get('a') == 5
    zone.get('b') == 10


def test_zone_check(zone: Zone, buckets: Buckets):
    buckets['a'] = 0
    buckets['b'] = 0.5
    buckets['c'] = 1.5
    assert not zone.check('a')
    assert not zone.check('b')
    assert zone.check('c')
    assert zone.check('d')


def test_zone_increment(zone: Zone, buckets: Buckets):
    zone.increment('a')
    assert buckets['a'] == 9.0


def test_zone_limit(zone: Zone, buckets: Buckets):
    buckets['a'] = 0
    assert zone.limit('a')
    assert not zone.limit('b')
    assert buckets['a'] == 0
    assert buckets['b'] == 9


def test_zone_hard_limit(zone: Zone, buckets: Buckets):
    buckets['a'] = 0
    with pytest.raises(LimitExceededException):
        zone.hard_limit('a')
    assert buckets['a'] == 0

    zone.hard_limit('b')
    assert buckets['b'] == 9
