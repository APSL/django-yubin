#!/usr/bin/env python
# encoding: utf-8
# ----------------------------------------------------------------------------

EMAIL_PORT = 1025
ROOT_URLCONF = 'tests.urls'

SECRET_KEY = 'yo secret yo'
SITE_ID = 1

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django_yubin',
    'tests.app',
)
