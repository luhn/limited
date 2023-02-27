try:
    from redis import Redis
except ImportError:
    raise ImportError('Must have redis installed to use redis backend.')

from ..zone import Zone
from .backend import Backend


class RedisBackend(Backend):
    SETTINGS = {
        'redis_url': str,
    }

    prefix: str

    def __init__(self, redis_url: str):
        redis = Redis.from_url(redis_url)
        self.prefix = 'limited'
        self.count_func = redis.register_script(REDIS_COUNT)
        self.remove_func = redis.register_script(REDIS_REMOVE)

    def _key(self, zone: Zone, key: str) -> str:
        return f'{self.prefix}:{zone.name}:{key}'

    def count(self, zone: Zone, identity: str) -> float:
        key = self._key(zone, identity)
        value = self.count_func(
            keys=[key],
            args=[zone.rate.per_second, zone.rate.count],
        )
        assert isinstance(value, float)
        return value

    def remove(self, zone: Zone, identity: str, count: int) -> bool:
        key = self._key(zone, identity)
        value = self.remove_func(
            keys=[key],
            args=[zone.rate.per_second, zone.rate.count, count],
        )
        return bool(value)


COUNT_FUNC = """
local function get_time()
    local value = redis.call('TIME')
    return tonumber(value[1]) + tonumber(value[2]) / 1000000
end

local now = get_time()

local function count(key, rate, size)
    local value = redis.call('GET', key)
    if (value == false) then
        return size
    end

    local split = string.gmatch(value, "%S+")
    local last_updated = tonumber(split())
    local tokens = tonumber(split())
    return math.min(tokens + (now - last_updated) * rate, size)
end
"""

REDIS_COUNT = COUNT_FUNC + """

local rate = tonumber(ARGV[1])
local size = tonumber(ARGV[2])
return count(KEYS[1], rate, size)
"""

REDIS_REMOVE = COUNT_FUNC + """

local rate = tonumber(ARGV[1])
local size = tonumber(ARGV[2])
local to_remove = tonumber(ARGV[3])
local tokens = count(KEYS[1], rate, size)
if (tokens < to_remove) then
    return 0
end

tokens = tokens - to_remove
local value = now .. ' ' .. tokens
local ex = math.ceil(now + (size - tokens) / rate)
redis.call('SET', KEYS[1], value, 'EX', ex)
return 1
"""
