from .backend import Backend, load_backend, Setting
from typing import Mapping, Any
from .zone import Zone


class Limited:
    backends: Mapping[str, Backend]
    zones: Mapping[str, Zone]


settings = {
    'backends': {
        'default': {
            'backend': 'redis',
            'redis_url': 'redis://',
        },
    },
    'zones': {
        'zone': '12/s',
        'register': {
            'rate': '12/h',
            'backend': 'foo',
        },
    },
}


def settings_from_env():





def _backends_from_env():
    backends = dict()
    PREFIX = 'LIMIT_BACKEND_'
    SUFFIX = '_BACKEND'
    items = [
        (k, v) for (k, v) in os.environ.items()
        if k.startswith('LIMIT_BACKEND_')
        and k.endswith('_BACKEND')
    ]
    for k, v in items:
        name = k[len(PREFIX):(len(k) - len(SUFFIX))].lower()
        backends[name] = _backend_from_env(name, v)


def _backend_from_env(name: str, backend_name: str):
    Backend = load_backend(backend_name)
    settings: dict[str, str] = dict()
    for k in Backend.SETTINGS.keys():
        env_name = f'LIMIT_BACKEND_{backend_name.upper()}_{k.upper()}'
        settings[k] = os.environ.get(env_name, Setting.MISSING)
    parsed = parse_settings(Backend.SETTINGS, settings)




LIMIT_BACKEND_TEST_BACKEND=redis
LIMIT_BACKEND_TEST_REDIS_URL=redis://

LIMIT_DEFAULT_BACKEND=test

LIMIT_ZONE_LOGIN=12/s
LIMIT_ZONE_REGISTER=12/h
LIMIT_ZONE_REGISTER_BACKEND=test


limit.backend.test = redis
limit.backend.test.redis_url = redis://

limit.default_backend = test

limit.zone.login = 12/s
limit.zone.register = 12/h
limit.zone.register.backend = test
