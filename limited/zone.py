from dataclasses import dataclass

from .backend import Backend
from .rate import Rate


@dataclass(frozen=True)
class Zone:
    name: str
    rate: Rate
    backend: Backend
