import pytest


def pytest_addoption(parser):
    parser.addoption(
        '--run-integration', action='store_true', default=False,
        help='run integration tests'
    )
    parser.addoption(
        '--redis-url', action='store', default='redis://',
        help='URL for connecting to redis.'
    )


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        'integration: mark test as an integration, which will not run by '
        'default.'
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption('--run-integration'):
        return
    skip_integration = pytest.mark.skip(
        reason='need --run-integration option to run'
    )
    for item in items:
        if 'integration' in item.keywords:
            item.add_marker(skip_integration)
