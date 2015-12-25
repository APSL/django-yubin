============
Contributing
============

This section of the docs is work in progress.


Running the tests
=================

You'll need to run a dummy mail server for some of the tests. You can do this
by executing::

    $ ./bin/fake-server

This will start a fake server in the shell. You could background this task if
you wish, or just run it in a separate shell screen/tab.

Next, to actually run the tests, you need ``tox``::

    $ pip install tox

.. note:: You can also install ``detox`` to parallelize the tests for different
   versions.

Execute ``tox`` to run all the build matrix. This will run the tests for any
of the Python versions you have installed in your system (Python 2.7, 3.2 until
3.5 and PyPy). If you don't have all versions, these builds will be skipped::

    $ tox

Run ``detox`` if you prefer parallelizing. To run a single environment, you have
some options::

    $ tox -e py27-django19  # run Python 2.7 and Django 1.9

or, in a virtualenv for example::

    $ python runtests.py

If you need to dive into a single test file or test case, you can also run the
tests via ``manage.py``::

    $ python tests/manage.py test tests.tests.test_backend.TestBackend
