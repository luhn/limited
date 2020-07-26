from dataclasses import dataclass


@dataclass(frozen=True)
class Rate:
    count: int
    time: float


def parse_rate(s: str) -> Rate:
    return None
