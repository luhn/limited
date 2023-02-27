import importlib
from typing import Dict, Type

from .backend import Backend


BUILTIN_BACKENDS: Dict[str, str] = {
    'memory': '.memory.MemoryBackend',
    'redis': '.redis.RedisBackend',
    'dynamodb': '.dynamodb.DynamoDBBackend',
}


def load_backend(backend: str | Type[Backend]) -> Type[Backend]:
    """
    Load a backend by name.  Can either be the name of a builtin backend or a
    fully qualified name of a function, e.g. ``myproject.module.MyBackend``.
    Available backends are:

    * ``simple``
    * ``memory``
    * ``redis``
    * ``dynamodb``

    """
    if isinstance(backend, type) and issubclass(backend, Backend):
        return backend
    elif isinstance(backend, str):
        try:
            backend = BUILTIN_BACKENDS[backend]
        except KeyError:
            raise ValueError(f'No such backend "{backend}"')
        p, m = backend.rsplit('.', 1)
        mod = importlib.import_module(p)
        attr = getattr(mod, m)
        if isinstance(attr, type) and issubclass(attr, Backend):
            return attr
        else:
            raise TypeError('Backend must be subclass of Backend class.')
    else:
        raise ValueError('Expecting string or Backend subclass.')


__all__ = [
    'load_backend',
    'Backend',
]
