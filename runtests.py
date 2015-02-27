#!/usr/bin/env python
# encoding: utf-8
# ----------------------------------------------------------------------------

import os
import sys

parent = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, parent)
os.environ['DJANGO_SETTINGS_MODULE'] = 'django_yubin.testapp.settings'


# Django 1.7 and later requires a separate .setup() call

import django
try:
    django.setup()
except AttributeError:
    pass

from django.test.simple import DjangoTestSuiteRunner

def runtests(*test_args):
    test_args = test_args or ['testapp']
    parent = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, parent)
    runner = DjangoTestSuiteRunner(verbosity=2, interactive=True,
                                   failfast=False)
    failures = runner.run_tests(test_args)
    sys.exit(failures)


if __name__ == '__main__':
    runtests()
