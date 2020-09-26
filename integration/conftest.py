import pytest


def pytest_addoption(parser):
    parser.addoption(
        '--backends', action='store', default='all',
        help='Comma-separated list of backends to test, or "all" to all '
        'backends.  Available backends are:  memory, redis'
    )
    parser.addoption(
        '--redis-url', action='store', default='redis://',
        help='URL for connecting to redis.'
    )


@pytest.fixture(scope='session')
def check_backend(request):
    """
    Returns a function to check if the given backend should run.

    """
    backends = request.config.getoption('--backends')
    if backends == 'all':
        def check_backend(name):
            pass

        return check_backend

    backends = backends.split(',')

    def check_backend(name):
        if name not in backends:
            pytest.skip(f'Backend {name} not in list.')

    return check_backend
