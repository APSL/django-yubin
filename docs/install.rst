============
Installation
============

An obvious prerequisite of django-yubin is Django - 1.3 is the
minimum supported version.


Installing django_yubin
==========================

Download and install from http://github.com/APSL/django-yubin.git

If you're using pip__ and a virtual environment, this usually looks like::

    pip install -e git+http://github.com/APSL/django-yubin.git#egg=django-yubin

.. __: http://pip.openplans.org/

Or for a manual installation, once you've downloaded the package, unpack it
and run the ``setup.py`` installation script::

    python setup.py install


Configuring your project
========================

In your Django project's settings module, add django_yubin to your
``INSTALLED_APPS`` setting::
    
    INSTALLED_APPS = (
        ...
        'django_yubin',
    )



Note that django yubin doesn't implicitly queue all django mail (unless you
tell it to).

To queue all django mail you must configure the mail backend as::

    EMAIL_BACKEND = 'django_yubin.smtp_queue.EmailBackend'

More details can be found in the queue documentation.
