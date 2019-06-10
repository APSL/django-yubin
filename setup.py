#!/usr/bin/env python
# encoding: utf-8
# ----------------------------------------------------------------------------

from setuptools import setup


INSTALL_REQUIRES = [
    'pyzmail;python_version<"3.6"',
    'pyzmail36;python_version>="3.6"',
    'lockfile',
    'pytz',
]

TEST_REQUIREMENTS = [
    'six'
]


with open('docs/index.rst') as docs_index:
    long_description = docs_index.read()


setup(
    name='django-yubin',
    version='1.4.0',
    description=("A reusable Django app for composing and queueing emails "
                 "Adds django-mailer2 + django-mailviews + others"),
    long_description=long_description,
    author='Antoni Aloy',
    author_email='aaloy@apsl.net',
    url='http://github.com/APSL/django-yubin',
    install_requires=INSTALL_REQUIRES,
    packages=[
        'django_yubin',
        'django_yubin.management',
        'django_yubin.management.commands',
        'django_yubin.migrations',
    ],
    include_package_data=True,
    # tests
    tests_require=TEST_REQUIREMENTS,
    test_suite='runtests.runtests',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Framework :: Django',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
    ]
)
