Contributing
============

django-yubin is an open source project and improvements and bug reports are very appreciated.

You can contribute in many ways:

* Filling a bug on github.
* Creating a patch and sending the pull request.
* Help on testing and documenting.

When sending a pull request, please be sure that all tests and builds passes. In the next section
you'll find information about how to write and run tests.

Please, follow the `PEP8 <https://peps.python.org/pep-0008/>`_ coventions and in case you write
additional features don't forget to write tests for them.

At `APSL <https://apsl.net/en/>`_ we use yubin for most of our own projects, so we'll try to
mantain it as bug free and stable as possible. That said, we can't not guarantee that we could
patch the program in the way you like, add that new feature, etc.


Demo Project
------------

A demo/development project is provided in the ``demo`` directory. It is usefull during development
for manual tests, checks and the admin site.

The project has a `Docker Compose <https://docs.docker.com/compose/>`_ file with all the
development infrastructure needed: a Postgres database, a Redis server for Celery tasks and a SMTP
server that prints emails in the terminal.

Also, you will need `Pipenv <https://pipenv.pypa.io/>`_ to manage Python dependencies and
virtualenv.

**Usage**

* Create virtualenv and install dependencies

  .. code:: bash

    $ cd demo
    $ python3 -m venv .venv
    $ source .venv/bin/activate
    $ pip install -r requirements.txt

* Start servers

  .. code:: bash

    $ docker compose up -d

* The first time you need to run database migrations and create a superuser

  .. code:: bash

    $ python manage.py migrate
    $ python manage.py createsuperuser

* Start the development server

  .. code:: bash

    $ python manage.py runserver

* In another terminal, start a Celery worker and a Celery Beat scheduler

  .. code:: bash

    $ celery -A demo.celery worker -l info -B

Now you can open http://localhost:8000 in your browser and see the demo project running.

Once yo have finished, to stop everything you can:

* Press Ctrl+C to stop the ``runserver`` and the Celery worker.
* Run `$ docker compose down` to stop all the servers.


Tests
-----

To run the tests you need a Python environment with the test dependencies. The easiest way is to
use the same virtualenv that you have created for the demo project, it already has the test
dependencies.

Once you are in the demo virtual environment, you can go to the root directory and run tests from
there. Let's see a couple of examples:

.. code:: bash

  # Run all tests with you current python environment
  $ ./runtests.py

  # Run specific tests with you current python environment
  $ ./runtests.py tests.tests.test_backend

  # Use tox to run all tests with all available Python environments and see a
  # code coverage report
  $ tox

  # The same but only for a specific subset of tests
  $ tox -- tests.tests.test_backend


CI/CD
-----

Continuous integration and deployment are done using
`Github Actions <https://docs.github.com/en/actions>`_. Right now it runs tests and code coverage
with Tox in PRs and pushes to `master` branch.

Please, be sure that everything is green before sending PRs.

Feel free to add yourself to ``humans.txt`` file in your PR.


Documentation
-------------

This documentation is built with `Sphinx <https://www.sphinx-doc.org>`_ and is available at
`Read the Docs <https://django-yubin.readthedocs.io/>`_.
