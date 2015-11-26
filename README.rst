.. image:: https://img.shields.io/travis/ExCiteS/geokey-airquality/master.svg
    :alt: Travis CI Build Status
    :target: https://travis-ci.org/ExCiteS/airquality

.. image:: https://img.shields.io/coveralls/ExCiteS/airquality/master.svg
    :alt: Coveralls Test Coverage
    :target: https://coveralls.io/r/ExCiteS/airquality

geokey-airquality
=================

`GeoKey <https://github.com/ExCiteS/geokey>`_ (v0.8+ only) extension for `Air Quality <https://github.com/ExCiteS/airquality>`_ functionality.

Install
-------

Install from cloned repository:

.. code-block:: console

    git clone https://github.com/ExCiteS/geokey-airquality.git
    cd geokey-airquality
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

You're now ready to go!

Test
----

Run tests:

.. code-block:: console

    python manage.py test geokey_airquality

Check code coverage:

.. code-block:: console

    coverage run --source=geokey_airquality manage.py test geokey_airquality
    coverage report -m --omit=*/tests/*,*/migrations/*
