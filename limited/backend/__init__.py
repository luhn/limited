import importlib
from typing import Dict, Type, cast

from .backend import Backend
from .setting import Setting
from .memory import MemoryBackend
from .redis import RedisBackend


BUILTIN_BACKENDS: Dict[str, Type[Backend]] = {
    'memory': MemoryBackend,
    'redis': RedisBackend,
    # 'dynamodb': DynamoDBBackend,
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
    backend = BUILTIN_BACKENDS.get(name, name)
    if issubclass(backend, Backend):
        return backend
    elif isinstance(backend, str):
        p, m = backend.rsplit('.', 1)
        mod = importlib.import_module(p)
        attr = getattr(mod, m)
        if issubclass(attr, Backend):
            return attr
        else:
            raise TypeError('Backend must be subclass of Backend class.')
    else:
        raise ValueError('Expecting string or Backend subclass.')


__all__ = [
    'load_backend',
    'Backend',
]
