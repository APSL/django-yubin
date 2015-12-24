#!/usr/bin/env python
# encoding: utf-8
# ----------------------------------------------------------------------------

import os
import sys


def runtests(*args):
    test_dir = os.path.dirname(__file__)
    sys.path.insert(0, test_dir)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'

    import django
    from django.test.utils import get_runner
    from django.conf import settings

    django.setup()  # only 1.7 and up are supported

    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=True, failfast=False)
    failures = test_runner.run_tests(args)
    sys.exit(failures)


if __name__ == '__main__':
    # TODO: forward sys.argv?
    runtests()
