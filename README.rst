.. image:: https://img.shields.io/pypi/v/geokey-airquality.svg
    :alt: PyPI Package
    :target: https://pypi.python.org/pypi/geokey-airquality

.. image:: https://img.shields.io/travis/ExCiteS/geokey-airquality/master.svg
    :alt: Travis CI Build Status
    :target: https://travis-ci.org/ExCiteS/geokey-airquality

.. image:: https://img.shields.io/coveralls/ExCiteS/geokey-airquality/master.svg
    :alt: Coveralls Test Coverage
    :target: https://coveralls.io/r/ExCiteS/geokey-airquality

geokey-airquality
=================

`GeoKey <https://github.com/ExCiteS/geokey>`_ extension for `Air Quality <https://github.com/ExCiteS/airquality>`_ functionality.

Install
-------

geokey-airquality requires:

- Python version 2.7
- GeoKey version 1.0

Install the geokey-airquality from PyPI:

.. code-block:: console

    pip install geokey-airquality

Or from cloned repository:

.. code-block:: console

    cd geokey-airquality
    pip install -e .

Add the package to installed apps:

.. code-block:: python

    INSTALLED_APPS += (
        ...
        'geokey_airquality',
    )

Migrate the models into the database:

.. code-block:: console

    python manage.py migrate geokey_airquality

Copy static files:

.. code-block:: console

    python manage.py collectstatic

Setup a Cron job for checking measurements that due to finish by running:

.. code-block:: console

    crontab -e

And adding:

.. code-block:: console

    15 0 * * * python local_settings/manage.py check_measurements

You're now ready to go!

Update
------

Update the geokey-airquality from PyPI:

.. code-block:: console

    pip install -U geokey-airquality

Migrate the models into the database:

.. code-block:: console

    python manage.py migrate geokey_airquality

Copy static files:

.. code-block:: console

    python manage.py collectstatic

Develop & Test
--------------

Clone the repository:

.. code-block:: console

    git clone git@github.com:ExCiteS/geokey-airquality.git

Install the extension for development:

.. code-block:: console

    cd geokey-airquality
    pip install -e .

Add the package to installed apps:

.. code-block:: python

    INSTALLED_APPS += (
        ...
        'geokey_airquality',
    )

Migrate the models into the database:

.. code-block:: console

    python manage.py migrate geokey_airquality

Copy static files:

.. code-block:: console

    python manage.py collectstatic

When database structure has changed, make migrations file (migrate after that to alter local database):

.. code-block:: console

    python manage.py makemigrations geokey_airquality

Run tests:

.. code-block:: console

    python manage.py test geokey_airquality

Check code coverage:

.. code-block:: console

    coverage run --source=geokey_airquality manage.py test geokey_airquality
    coverage report -m --omit=*/tests/*,*/migrations/*

API
---

Sign the request with the OAuth access token to authenticate a user.

**Sends a CSV sheet via email:**

.. code-block:: console

    GET /api/airquality/sheet/

**Get added projects:**

.. code-block:: console

    GET /api/airquality/projects/

Response:

.. code-block:: console

    [
        {
            "id": 12,
            "name": "Air Quality in London"
        }
    ]

**Get personal added locations:**

.. code-block:: console

    GET /api/airquality/locations/

Response:

.. code-block:: console

    [
        {
            "id": 115,
            "type": "Feature",
            "geometry": {
                // GeoJSON point
            },
            "name": "South Bank",
            "created": "2015-09-15T09:40:01.747Z",
            "properties": {
                "height": 2 // height from ground
                "distance": 3.5 // distance from road,
                "characteristics": null // site characteristics
            },
            "measurements": [
                // a list of measurements
            ]
        }
    ]

**Add new location**

.. code-block:: console

    POST /api/airquality/locations/

Request body:

.. code-block:: console

    {
        "type": "Feature",
        "geometry": {
            // GeoJSON point
        },
        "name": "My new location",
        "properties": {
            "height": 4.2,
            "distance": 7
        }
    }

Response:

.. code-block:: console

    {
        "id": 117,
        "type": "Feature",
        "geometry": {
            // GeoJSON point
        },
        "name": "My new location",
        "created": "2015-09-22T07:22:08.147Z",
        "properties": {
            "height": 4.2,
            "distance": 7,
            "characteristics": null
        },
        "measurements": []
    }

**Update your location:**

.. code-block:: console

    PATCH /api/airquality/locations/:location_id/

Request body:

.. code-block:: console

    {
        "type": "Feature",
        "geometry": {
            // GeoJSON point
        },
        "name": "My updated location",
        "properties": {
            "height": 4.2,
            "distance": 12
        }
    }

Response:

.. code-block:: console

    {
        "id": 117,
        "type": "Feature",
        "geometry": {
            // GeoJSON point
        },
        "name": "My updated location",
        "created": "2015-09-22T07:22:08.147Z",
        "properties": {
            "height": 4.2,
            "distance": 12,
            "characteristics": null
        },
        "measurements": []
    }

**Delete your location:**

.. code-block:: console

    DELETE /api/airquality/locations/:location_id/

**Add new measurement to your location**

.. code-block:: console

    POST /api/airquality/locations/:location_id/measurements/

Request body:

.. code-block:: console

    {
        "barcode": 145023
        "called": "2015-12-22T07:08:08.121Z",
        "started": "2015-12-23T09:12:02.247Z"
    }

Response:

.. code-block:: console

    {
        "id": 115,
        "barcode": "145023",
        "started": "2015-12-23T09:12:02.247Z",
        "finished": null,
        "properties": {
            "results": null, // measurement results
            "additional_details": null // additional details (per measurement)
        }
    }

**Update your measurement:**

.. code-block:: console

    PATCH /api/airquality/locations/:location_id/measurements/:measurement_id/

Request body:

.. code-block:: console

    {
        "barcode": 145023,
        "called": "2015-12-23T09:22:01.147Z",
        "finished": "2015-12-23T09:22:01.147Z",
        "project": "45",
        "properties": {
            "results": 64.78,
            "additional_details": null
        }
    }

If "finished" is being described, "called" should be also present to calculate actual time difference. Otherwise current time will be used.

If measurement has "started", "finished" and "results" collected, it is still saved until "project" is being attached to measurement. When attached, a new contribution gets created, also current measurement is removed completely.

Response (when no project):

.. code-block:: console

    {
        "id": 154,
        "barcode": "451001",
        "started": "2015-11-29T12:01:04.178Z",
        "finished": "2015-12-23T09:22:01.147Z",
        "properties": {
            "results": 64.78,
            "additional_details": null
        }
    }

**Delete your measurement:**

.. code-block:: console

    DELETE /api/airquality/locations/:location_id/measurements/:measurement_id/
