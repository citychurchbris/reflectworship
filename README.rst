Reflect Worship
---------------

Development requirements
========================

* Python 3.6
* PostgreSQL
* pyenv_
* direnv_ (recommended)


Development setup
=================

#. Check out the repo:

   .. code:: sh

      git clone git@github.com:citychurchbris/reflectworship.git

#. Set up a local Postgres database and user.

   .. code:: sh

      # Create new user with 'create' privileges (for tests)
      createuser reflect --pwprompt --createdb
      # Create new db owned by the user
      createdb -O reflect reflect

#. Set up the following development environment variables (we recommend using direnv_ and an `.envrc` file):

   .. code:: sh

    export DJANGO_SECRET_KEY=<a-long-secret-key>
    export DJANGO_DEBUG=True
    export DATABASE_URL="postgres://reflect:DATABASE_PASSWORD@localhost/reflect"
    export DISABLE_SSL=True
    export ROOT_URL=http://127.0.0.1:8000

#. Build

   .. code:: sh

        cd reflect
        make dev

   (This will create you a virtualenv, and install all dependencies)

#. Collect static assets

   .. code:: sh

        ./venv/bin/python manage.py collectstatic

#. Run tests

   .. code:: sh

        make test

#. Run local database migrations

   .. code:: sh

        ./venv/bin/python manage.py migrate

#. Set up admin user

   .. code:: sh

        ./venv/bin/python manage.py createsuperuser

#. Run local server

   .. code:: sh

        ./venv/bin/python manage.py runserver


Deployment
==========

Currently, the admin app is deployed to Heroku. The makefile has a recipe for
adding the necessary git remotes;

  .. code:: sh

    make heroku-setup

.. _pyenv: https://github.com/pyenv/pyenv
.. _direnv: https://direnv.net/
