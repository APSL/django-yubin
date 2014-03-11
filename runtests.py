#!/usr/bin/env python
# encoding: utf-8
# ----------------------------------------------------------------------------

import os
import sys

parent = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, parent)
os.environ['DJANGO_SETTINGS_MODULE'] = 'django_yubin.testapp.settings'

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
