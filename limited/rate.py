import re
from datetime import timedelta as TimeDelta


SECOND = TimeDelta(seconds=1)
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR
WEEK = 7 * DAY
MONTH = 31 * DAY
YEAR = 365 * DAY

MILLISECOND = SECOND / 1000

UNITS: dict[str, TimeDelta] = {
    'ms': MILLISECOND,
    'millisecond': MILLISECOND,
    'milliseconds': MILLISECOND,
    's': SECOND,
    'second': SECOND,
    'seconds': SECOND,
    'm': MINUTE,
    'minute': MINUTE,
    'minutes': MINUTE,
    'h': HOUR,
    'hour': HOUR,
    'hours': HOUR,
    'd': DAY,
    'day': DAY,
    'days': DAY,
    'w': WEEK,
    'week': WEEK,
    'weeks': WEEK,
    'm': MONTH,
    'month': MONTH,
    'months': MONTH,
    'y': YEAR,
    'year': YEAR,
    'years': YEAR,
}


class Rate:
    REGEX = r'(?P<count>[0-9]+)/(?P<duration>[0-9]*)(?P<unit>[a-zA-Z]+)'

    def __init__(self, count: int, duration: TimeDelta):
        self.count = count
        self.duration = duration

    @classmethod
    def from_string(cls, s: str):
        m = self.REGEX.match(s)
        if m is None:
            raise ValueError(f'"{s}" is not a valid rate string.')
        count = int(m.group('count'))
        unit_str = m.group('unit').lower()
        if unit_str not in UNITS:
            raise ValueError('"{unit_str}" is not a valid unit.')
        unit = UNITS[unit_str]
        duration = int(m.group('duration') or 1)
        return cls(count, duration * unit)

    @property
    def per_second(self) -> float:
        return self.count / self.duration.total_seconds()

    def __mul__(self, val: int | float | TimeDelta) -> float:
        if isinstance(val, TimeDelta):
            val = val.total_seconds()
        return val * self.per_second()
