from geokey.extensions.base import register


VERSION = (0, 1, 2)
__version__ = '.'.join(map(str, VERSION))

register(
    'geokey_airquality',
    'Air Quality',
    display_admin=True,
    superuser=True,
    version=__version__
)
