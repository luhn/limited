from redis import Redis
from redis.client import Script

from .backend import Backend
from .zone import Zone


class RedisBackend(Backend):
    def __init__(self, redis_url: str):
        redis = Redis.from_url(redis_url)
        self.count_func = redis.register_script(REDIS_COUNT)
        self.remove_func = redis.register_script(REDIS_REMOVE)

    def __call__(self, name: str, rate: float, size: int) -> Zone:
        return RedisZone(name, rate, size, self.count_func, self.remove_func)

    @classmethod
    def from_env(cls, environ) -> 'RedisBackend':
        pass

    @classmethod
    def from_ini(cls, settings) -> 'RedisBackend':
        pass


class RedisZone(Zone):
    def __init__(self, name: str, rate: float, size: int, count_func:
                 Script, remove_func: Script):
        self.name = name
        self.rate = rate
        self.size = size
        self.count_func = count_func
        self.remove_func = remove_func

    def _key(self, key: str) -> str:
        return f'{self.name}:{key}'

    def count(self, key: str) -> int:
        value = self.count_func(keys=[key], args=[self.rate, self.size])
        return int(value)

    def remove(self, key: str, count: int) -> bool:
        value = self.remove_func(
            keys=[key],
            args=[self.rate, self.size, count],
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
