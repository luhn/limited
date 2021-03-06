import secrets
from time import sleep

import pytest


@pytest.fixture(scope='session')
def memory_backend(check_backend):
    check_backend('memory')

    from limited.backend.memory import MemoryBackend
    return MemoryBackend(100)


@pytest.fixture(scope='session')
def redis_backend(request, check_backend):
    check_backend('redis')

    from limited.backend.redis import RedisBackend
    url = request.config.getoption('--redis-url')
    return RedisBackend(url)


@pytest.mark.parametrize('backend', [
    pytest.lazy_fixture('memory_backend'),
    pytest.lazy_fixture('redis_backend'),
])
def test_integration(backend):
    zone = backend('mybackend', 1.0, 10)
    identity = secrets.token_urlsafe()
    assert zone.count(identity) == 10.0
    assert zone.remove(identity, 5)
    assert 4.5 < zone.count(identity) < 5.5
    sleep(1.0)
    assert 5.5 < zone.count(identity) < 6.5
