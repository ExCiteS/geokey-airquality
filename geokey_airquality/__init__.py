"""Main initialisation for extension."""

VERSION = (1, 1, 1)
__version__ = '.'.join(map(str, VERSION))


try:
    from geokey.extensions.base import register

    register(
        'geokey_airquality',
        'Air Quality',
        display_admin=True,
        superuser=True,
        version=__version__
    )
except BaseException:
    print 'Please install GeoKey first'
