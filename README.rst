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

Develop and Test
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

Get **added projects**:

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

Get **your added locations**:

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
