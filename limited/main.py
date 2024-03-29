from ipaddress import IPv4Address, IPv6Address, IPv6Network, ip_address
from typing import Mapping

from .backend import Backend, load_backend
from .exceptions import LimitExceeded
from .rate import Rate
from .settings import Settings
from .zone import Zone


class Limited:
    def __init__(
        self,
        backends: Mapping[str, Backend],
        zones: Mapping[str, Zone],
        ipv6_prefix: int = 56,
        ipv6_prefix_scale_factor: int = 8,
        ipv6_rate_scale_factor: int = 4,
        ipv6_scale_count: int = 3,
    ):
        self.backends = backends
        self.zones = zones
        self.ipv6_prefix = ipv6_prefix
        self.ipv6_prefix_scale_factor = ipv6_prefix_scale_factor
        self.ipv6_rate_scale_factor = ipv6_rate_scale_factor
        self.ipv6_scale_count = ipv6_scale_count

    @classmethod
    def from_settings(cls, settings: Settings):
        backends: dict[str, Backend] = dict()
        for name, backend_settings in settings['backends'].items():
            if isinstance(backend_settings, Backend):
                backends[name] = backend_settings
            else:
                backend_name = backend_settings.pop('backend')  # type: ignore
                _Backend = load_backend(backend_name)
                backends[name] = _Backend(**backend_settings)  # type: ignore
        default_backend = backends.get('default')

        zones: dict[str, Zone] = dict()
        for name, zone_settings in settings['zones'].items():
            rate: Rate | str
            if isinstance(zone_settings, (str, Rate)):
                if default_backend is None:
                    raise ValueError('Default backend is not defined.')
                backend = default_backend
                rate = zone_settings
            elif isinstance(zone_settings, Mapping):
                try:
                    backend = backends[zone_settings.get('backend', 'default')]
                except KeyError:
                    raise ValueError(f'No such backend "{backend}"')
                rate = zone_settings['rate']
            else:
                raise ValueError()
            if isinstance(rate, str):
                _rate = Rate.from_string(rate)
            else:
                _rate = rate
            zones[name] = Zone(name=name, backend=backend, rate=_rate)
        KEYS = [
            'ipv6_prefix', 'ipv6_prefix_scale_factor',
            'ipv6_rate_scale_factor', 'ipv6_scale_count',
        ]
        kwargs = {}
        for key in KEYS:
            if key in settings:
                kwargs[key] = settings[key]  # type: ignore
        return cls(
            backends=backends,
            zones=zones,
            **kwargs,
        )

    def get_zone(self, zone: str | Zone) -> Zone:
        if isinstance(zone, Zone):
            return zone
        elif isinstance(zone, str):
            try:
                return self.zones[zone]
            except KeyError:
                raise ValueError(f'No such zone "{zone}"')
        else:
            raise TypeError('`zone` must be string or Zone type.')

    def limit(self, zone: str | Zone, key: str, hard: bool = False) -> bool:
        zone = self.get_zone(zone)
        if not zone.backend.remove(zone, key, 1):
            if hard:
                raise LimitExceeded()
            else:
                return False
        return True

    def increment(self, zone: str | Zone, key: str, count: int = 1) -> None:
        zone = self.get_zone(zone)
        zone.backend.remove(zone, key, 1)

    def check(self, zone: str | Zone, key: str) -> bool:
        zone = self.get_zone(zone)
        return zone.backend.count(zone, key) >= 1

    def limit_by_ip(
            self,
            zone: str | Zone,
            ip: str | IPv4Address | IPv6Address,
            hard: bool = False,
    ):
        if isinstance(ip, str):
            ip = ip_address(ip)
        if isinstance(ip, IPv4Address):
            return self.limit_by_ipv4(zone, ip, hard=hard)
        elif isinstance(ip, IPv6Address):
            return self.limit_by_ipv6(zone, ip, hard=hard)
        else:
            raise TypeError(
                '`ip` must be one of str, IPv4Address, or IPv6Address'
            )

    def limit_by_ipv4(
            self,
            zone: str | Zone,
            ip: str | IPv4Address,
            hard: bool = False,
    ):
        return self.limit(zone, str(ip), hard=hard)

    def limit_by_ipv6(
            self,
            zone: str | Zone,
            ip: str | IPv6Address,
            hard: bool = False,
    ):
        zone = self.get_zone(zone)
        net = IPv6Network(ip).supernet(new_prefix=self.ipv6_prefix)
        for i in range(self.ipv6_scale_count):
            # For each scale factor, calculate the new network and rate, then
            # create a virtual zone and run the rate limit.
            key = str(net.supernet(i * self.ipv6_prefix_scale_factor))
            count = zone.rate.count * i * self.ipv6_prefix_scale_factor
            rate = Rate(count=count, duration=zone.rate.duration)
            _zone = Zone(name=zone.name, rate=rate, backend=zone.backend)
            if not self.limit(_zone, key, hard=hard):
                return False
        return True
