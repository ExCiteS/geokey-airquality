.. image:: https://img.shields.io/travis/ExCiteS/geokey-airquality/master.svg
    :alt: Travis CI Build Status
    :target: https://travis-ci.org/ExCiteS/geokey-airquality

.. image:: https://img.shields.io/coveralls/ExCiteS/geokey-airquality/master.svg
    :alt: Coveralls Test Coverage
    :target: https://coveralls.io/r/ExCiteS/geokey-airquality

geokey-airquality
=================

`GeoKey <https://github.com/ExCiteS/geokey>`_ (v0.8+ only) extension for `Air Quality <https://github.com/ExCiteS/airquality>`_ functionality.

Install
-------

Install the extension:

.. code-block:: console

    pip install git+https://github.com/ExCiteS/geokey-airquality.git

Add the package to installed apps:

.. code-block:: console

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

Update the extension:

.. code-block:: console

    pip install -U git+https://github.com/ExCiteS/geokey-airquality.git

Migrate the models into the database:

.. code-block:: console

    python manage.py migrate geokey_airquality

Copy static files:

.. code-block:: console

    python manage.py collectstatic

Develop And Test
----------------

Clone the repository:

.. code-block:: console

    git clone git@github.com:ExCiteS/geokey-airquality.git

Install the extension for development:

.. code-block:: console

    cd geokey-communitymaps
    pip install -e .

Add the package to installed apps:

.. code-block:: console

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

**Get dded projects:**

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
                // GeoJSON object
            },
            "name": "South Bank",
            "created": "2015-09-15T09:40:01.747Z",
            "properties": {
                "additional_details": "Busy location."
            },
            "measurements": [
                // a list of measurements
            ]
        }
    ]

**Delete your location:**

.. code-block:: console

    DELETE /api/airquality/locations/:location_id/

**Update your measurement:**

.. code-block:: console

    PATCH /api/airquality/locations/:location_id/measurement/:measurement_id/

Request body:

.. code-block:: console

    {
        "called": "2015-12-23T09:22:01.147Z",
        "finished": "2015-12-23T09:22:01.147Z",
        "project": "45",
        "properties": {
            "results": "64.78"
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
            "results": 64.78
        }
    }

**Delete your measurement:**

.. code-block:: console

    DELETE /api/airquality/locations/:location_id/measurement/:measurement_id/
