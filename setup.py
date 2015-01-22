#!/usr/bin/env python
# encoding: utf-8
# ----------------------------------------------------------------------------

from setuptools import setup
from django_yubin import get_version

setup(
    name='django-yubin',
    version=get_version(),
    description=("A reusable Django app for composing and queueing emails "
                 "Adds django-mailer2 + django-mailviews + others"),
    long_description=open('docs/index.rst').read(),
    author='Antoni Aloy',
    author_email='aaloy@apsl.net',
    url='http://github.com/APSL/django-yubin',
    install_requires = ["pyzmail", "lockfile"],
    packages=[
        'django_yubin',
        'django_yubin.management',
        'django_yubin.management.commands',
    ],
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
)
