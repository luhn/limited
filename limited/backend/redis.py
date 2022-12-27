try:
    from redis import Redis
    from redis.client import Script
except ImportError:
    raise ImportError('Must have redis installed to use redis backend.')

from .backend import Backend


class RedisZone(Backend):
    def __init__(self, rate: float, size: int, redis_url: str, **settings: Mapping[):
        redis = Redis.from_url(redis_url)
        self.count_func = redis.register_script(REDIS_COUNT)
        self.remove_func = redis.register_script(REDIS_REMOVE)
        self.name = name
        self.rate = rate
        self.size = size
        self.count_func = count_func
        self.remove_func = remove_func

    def _key(self, zone: str, key: str) -> str:
        return f'{self.name}:{zone}:{key}'

    def count(self, zone: str, key: str) -> int:
        value = self.count_func(keys=[key], args=[self.rate, self.size])
        return int(value)

    def remove(self, zone: str, key: str, count: int) -> bool:
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
