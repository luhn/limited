import os
from typing import Tuple

from .backend import Backend, Zone, load_backend


class Region:
    def __getitem__(self, key: str):
        pass


class EnvVarRegion:
    backend: Backend

    def __init__(self) -> None:
        _Backend = load_backend(os.environ['LIMITED_BACKEND'])
        self.backend = _Backend.from_env(os.environ)

    def __getitem__(self, key: str) -> Zone:
        try:
            rate_str = os.environ[f'LIMITED_{ key.upper() }']
        except KeyError:
            raise KeyError(f'No such zone named { key }')
        rate, size = parse_rate(rate_str)
        return self.backend(key, rate, size)


class IniRegion:
    def __init__(self, settings: dict):
        self.settings = settings
        Backend = load_backend(os.environ['LIMITED_BACKEND'])
        self.backend = Backend.from_env(os.environ)

    def __getitem__(self, key: str):
        pass


def parse_rate(rate_str) -> Tuple[float, int]:
    raise NotImplementedError()
