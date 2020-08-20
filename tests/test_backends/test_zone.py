from typing import Dict

import pytest

from limited import Zone
from limited.exceptions import LimitExceededException


class MockZone(Zone):
    buckets: Dict[str, int]

    def __init__(self, size: int = 10, rate: float = 1.0):
        self.rate = rate
        self.size = size
        self.buckets = dict()

    def count(self, key: str) -> int:
        return self.buckets[key]

    def remove(self, key: str, count: int) -> bool:
        if self.buckets[key] >= count:
            self.buckets[key] -= count
            return True
        else:
            return False


def test_zone_ttl():
    zone = MockZone(size=10, rate=2.0)
    assert zone.ttl == 5.0


def test_zone_check():
    zone = MockZone()
    zone.buckets['a'] = 5
    zone.buckets['b'] = 0
    assert zone.check('a')
    assert not zone.check('b')


def test_zone_increment():
    zone = MockZone()
    zone.buckets['a'] = 5
    zone.increment('a')
    assert zone.buckets['a'] == 4


def test_zone_limit():
    zone = MockZone()
    zone.buckets['a'] = 5
    zone.buckets['b'] = 0
    assert not zone.limit('a')
    assert zone.limit('b')
    assert zone.buckets['a'] == 4
    assert zone.buckets['b'] == 0


def test_zone_hard_limit():
    zone = MockZone()
    zone.buckets['a'] = 5
    zone.buckets['b'] = 0
    zone.hard_limit('a')
    with pytest.raises(LimitExceededException):
        zone.hard_limit('b')
