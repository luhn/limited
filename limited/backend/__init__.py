import importlib

from .interface import Backend, ZoneBackend


BUILTIN_BACKENDS = {
    'simple': 'limited.backends.memory.SimpleMemoryBackend'
    'memory': 'limited.backends.memory.MemoryBackend'
    'redis': 'limited.backends.redis.RedisBackend',
    'dynamodb': 'limited.backends.dynamodb.DynamoDBBackend',
}


def load_backend(name: str) -> type:
    """
    Load a backend by name.  Can either be the name of a builtin backend or a
    fully qualified name of a function, e.g. ``myproject.module.MyBackend``.
    Available backends are:

    * ``simple``
    * ``memory``
    * ``redis``
    * ``dynamodb``

    """
    name = BUILTIN_BACKENDS.get(name, name)
    p, m = name.rsplit('.', 1)
    mod = importlib.import_module(p)
    return getattr(mod, m)


__all__ = [
    'load_backend',
    'Backend',
    'ZoneBackend',
]
