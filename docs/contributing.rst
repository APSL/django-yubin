============
Contributing
============

django-yubin is an open source project and imporvements and bug reports are
very appreciated.

You can contribute in many ways:

* Filling a bug on github
* Creating a patch and sending the pull request
* Help on testing and documenting

When sending a pull request, please be sure that all tests and builds passes. On
the next section you'll find information about how to write the test.

Please follow the PEP8 coventions and in case you write additional features don't
forget to write the tests for them.

At http://apsl.net we use yubin for most of our own projects, so we'll try to
mantain it as bug free as stable as possible. That said we can't not guarantee
that we could patch the program in the way you like, add that new feature, etc.



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

    $ tox -e py36-dj111  # run Python 3.6 and Django 1.11

or, in a virtualenv for example::

    $ python runtests.py

If you need to dive into a single test file or test case, you can also run the
tests via ``manage.py``::

    $ python tests/manage.py test tests.tests.test_backend.TestBackend



Demo Project
============

A demo project is provided for manual tests and checks, specially for the admin
site. It is configured to send mails with the same mail fake-server used for
tests. Username and password for the superuser is "yubin".
