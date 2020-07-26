import os
from .rate import parse_limit
from .zone import Zone
from .backend import load_backend


class Region:
    def __getitem__(self, key: str):
        pass


class EnvVarRegion:
    def __init__(self):
        Backend = load_backend(os.environ['LIMITED_BACKEND'])
        self.backend = Backend.from_env(os.environ)

    def __getitem__(self, key: str):
        try:
            rate_str = os.environ[f'LIMITED_{ key.upper() }']
        except KeyError:
            raise KeyError(f'No such zone named { key }')
        rate = parse_limit(rate_str)
        return Zone(key, rate, self.backend)


class IniRegion:
    def __init__(self, settings: dict):
        self.settings = settings
        Backend = load_backend(os.environ['LIMITED_BACKEND'])
        self.backend = Backend.from_env(os.environ)

    def __getitem__(self, key: str):
        pass
