from geokey.extensions.base import register


register(
    'geokey_airquality',
    'Air Quality',
    display_admin=True,
    superuser=True
)
