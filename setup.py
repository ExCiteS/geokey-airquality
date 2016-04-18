#!/usr/bin/env python

"""GeoKey extension for Air Quality functionality."""

from os.path import join
from setuptools import setup, find_packages


name = 'geokey-airquality'
version = __import__(name.replace('-', '_')).__version__
repository = join('https://github.com/ExCiteS', name)

setup(
    name=name,
    version=version,
    description='GeoKey extension for Air Quality functionality',
    url=repository,
    download_url=join(repository, 'tarball', version),
    author='Mapping for Change',
    author_email='info@mappingforchange.org.uk',
    license='MIT',
    packages=find_packages(exclude=['*.tests', '*.tests.*', 'tests.*']),
    include_package_data=True,
    install_requires=[],
)
