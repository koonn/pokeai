# Add to import path:
# python setup.py develop

from setuptools import setup, find_packages

setup(
    name="pokeai",
    version="0.1",
    packages=find_packages(),
    test_suite='test'
)
