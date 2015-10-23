# geokey-airquality

## How to install

Install the extension:

```
pip install git+https://github.com/ExCiteS/geokey-airquality.git
```

Add the installed extension to `local_settings/settings.py`:

```
INSTALLED_APPS += (
  ...
  'geokey_airquality'
)
```

Add the required tables to the database (from the main GeoKey directory):

```
python manage.py migrate geokey_airquality
```

## How to update

Update the extension:

```
pip install -U git+https://github.com/ExCiteS/geokey-airquality.git
```

Add the required tables to the database (from the main GeoKey directory):

```
python manage.py migrate geokey_airquality
```

## How to prepare for development

Clone the repository:

```
git clone git@github.com:ExCiteS/geokey-airquality.git
```

Install the extension for development:

```
cd geokey-airquality
pip install -e .
```

Add the installed extension to `local_settings/settings.py`:

```
INSTALLED_APPS += (
  ...
  'geokey_airquality',
)
```

Add the required tables to the database (from the main GeoKey directory):

```
python manage.py migrate geokey_airquality
```

When database structure has changed, make migrations file (migrate after that to alter local database):

```
python manage.py makemigrations geokey_airquality
```
