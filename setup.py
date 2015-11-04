from setuptools import setup, find_packages


setup(
    name='geokey-airquality',
    version='0.1.0-beta.1',
    author='Julius Osokinas',
    author_email='j.osokinas@mappinforchange.org.uk',
    packages=find_packages(exclude=['*.tests', '*.tests.*', 'tests.*']),
    include_package_data=True,
)
