import os
from typing import TypedDict, NotRequired, Callable, Any
from .rate import Rate
from .backend import Backend


class ZoneSettings(TypedDict):
    backend: str | type[Backend]
    rate: str | Rate


class BackendSettings(TypedDict):
    backend: str | type[Backend]


class Settings(TypedDict):
    backends = dict[str, BackendSettings | Backend]
    zones = dict[str, ZoneSettings | str | Rate]
    ipv6_prefix: NotRequired[int]
    ipv6_prefix_scale_factor: NotRequired[int]
    ipv6_rate_scale_factor: NotRequired[int]
    ipv6_scale_count: NotRequired[int]


ENV_MAP: list[tuple[str, str, Callable[[str], Any]]] = {
    ('ipv6_prefix', 'LIMITED_IPV6_PREFIX', int),
    ('ipv6_prefix_scale_factor', 'LIMITED_IPV6_PREFIX_SCALE_FACTOR', int),
    ('ipv6_rate_scale_factor', 'LIMITED_IPV6_RATE_SCALE_FACTOR', int),
    ('ipv6_scale_count', 'LIMITED_IPV6_SCALE_COUNT', int),
}


def settings_from_env() -> Settings:
    settings: Settings = {
        'backends': backends_from_env(),
        'zones': zones_from_env(),
    }
    for name, env, cast in ENV_MAP:
        if env in os.environ:
            settings[name] = cast(os.environ(env))
    return settings


def backends_from_env() -> dict[str, BackendSettings]:
    backends = dict()
    PREFIX = 'LIMIT_BACKEND_'
    SUFFIX = '_BACKEND'
    keys = (
        k for k in os.environ.keys()
        if k.startswith(PREFIX) and k.endswith(SUFFIX)
    )
    for k in keys:
        name = k[len(PREFIX):(0 - len(SUFFIX))].lower()
        backends[name] = _backend_from_env(name)
    return backends


def _backend_from_env(name: str, backend_name: str) -> BackendSettings:
    prefix = f'LIMITED_BACKEND_{name.upper()}_'
    return {
        k[len(prefix):].lower(): v for (k, v) in os.environ.items()
        if k.starswith(prefix)
    }


def zones_from_env() -> dict[str, ZoneSettings]:
    PREFIX = 'LIMIT_ZONE_'
    BACKEND_SUFFIX = '_BACKEND'
    items = (
        (k, v) for (k, v) in os.environ.items()
        if k.startswith(PREFIX) and not k.endswith('_BACKEND')
    )
    zones: dict[str, ZoneSettings] = dict()
    for k, v in items:
        name = k[len(PREFIX):].lower()
        backend = os.environ.get(k + BACKEND_SUFFIX, 'default')
        zones[name] = {
            'rate': v,
            'backend': backend,
        }
    return zones


INI_MAP: list[tuple[str, str, Callable[[str], Any]]] = {
    ('ipv6_prefix', 'LIMITED_IPV6_PREFIX', int),
    ('ipv6_prefix_scale_factor', 'LIMITED_IPV6_PREFIX_SCALE_FACTOR', int),
    ('ipv6_rate_scale_factor', 'LIMITED_IPV6_RATE_SCALE_FACTOR', int),
    ('ipv6_scale_count', 'LIMITED_IPV6_SCALE_COUNT', int),
}


def settings_from_ini(ini: dict[str, str]) -> Settings:
    settings: Settings = {
        'backends': backends_from_ini(),
        'zones': zones_from_ini(),
    }
    for name, env, cast in INI_MAP:
        if env in ini:
            settings[name] = cast(ini[env])
    return settings


def backends_from_ini(ini: dict[str, str]) -> dict[str, BackendSettings]:
    backends = dict()
    PREFIX = 'limit.backend.'
    SUFFIX = '.backend'
    keys = (
        k for k in ini
        if k.startswith(PREFIX) and k.endswith(SUFFIX)
    )
    for k in keys:
        name = k[len(PREFIX):(0 - len(SUFFIX))]
        backends[name] = _backend_from_ini(name)
    return backends


def _backend_from_ini(
    ini: dict[str, str],
    name: str,
    backend_name: str,
) -> BackendSettings:
    prefix = f'limit.backend.{name}.'
    return {
        k[len(prefix):].lower(): v for (k, v) in ini.items()
        if k.starswith(prefix)
    }


def zones_from_ini(ini: dict[str, str]) -> dict[str, ZoneSettings]:
    PREFIX = 'limit.'
    BACKEND_SUFFIX = '.backend'
    items = (
        (k, v) for (k, v) in ini.items()
        if k.startswith(PREFIX) and not k.endswith('.backend')
    )
    zones: dict[str, ZoneSettings] = dict()
    for k, v in items:
        name = k[len(PREFIX):].lower()
        backend = os.environ.get(k + BACKEND_SUFFIX, 'default')
        zones[name] = {
            'rate': v,
            'backend': backend,
        }
    return zones
