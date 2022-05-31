#!/usr/bin/env python
# encoding: utf-8
# ----------------------------------------------------------------------------

from setuptools import setup


INSTALL_REQUIRES = [
    'celery>=5.0,<5.3',
    'mail-parser',
    'pytz',
]


with open('README.rst') as docs_index:
    long_description = docs_index.read()


setup(
    name='django-yubin',
    version='2.0.0',
    description=("A reusable Django app for composing and queueing emails "
                 "django-mailviews + Celery + others"),
    long_description=long_description,
    author='Antoni Aloy',
    author_email='aaloy@apsl.net',
    maintainer='APSL',
    maintainer_email='info@apsl.net',
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
    test_suite='runtests.runtests',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Framework :: Django :: 3.1',
        'Framework :: Django :: 3.2',
    ]
)
