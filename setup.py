from setuptools import find_packages, setup

VERSION = '0.1.0'

INSTALL_REQUIRES = []

EXTRAS_REQUIRE = {
    'memory': ['cachetools'],
}

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='limited',
    version=VERSION,
    description='Rate limit library with multiple backends',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/luhn/limited/',
    author='Theron Luhn',
    author_email='theron@luhn.com',
    packages=find_packages(),
    python_requires='>=3.5',
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
)
