import os

from .backend import Backend, load_backend
from .zone import Zone, parse_rate


class Region:
    def __getitem__(self, key: str):
        pass


class EnvVarRegion:
    backend: Backend

    def __init__(self) -> None:
        _Backend = load_backend(os.environ['LIMITED_BACKEND'])
        self.backend = _Backend.from_env(os.environ)

    def __getitem__(self, key: str):
        try:
            rate_str = os.environ[f'LIMITED_{ key.upper() }']
        except KeyError:
            raise KeyError(f'No such zone named { key }')
        rate, size = parse_rate(rate_str)
        backend = self.backend(key, rate, size)
        return Zone(key, backend)


class IniRegion:
    def __init__(self, settings: dict):
        self.settings = settings
        Backend = load_backend(os.environ['LIMITED_BACKEND'])
        self.backend = Backend.from_env(os.environ)

    def __getitem__(self, key: str):
        pass
