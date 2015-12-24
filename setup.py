#!/usr/bin/env python
# encoding: utf-8
# ----------------------------------------------------------------------------

from setuptools import setup


INSTALL_REQUIRES = [
    'pyzmail',
    'lockfile',
]


with open('docs/index.rst') as docs_index:
    long_description = docs_index.read()


setup(
    name='django-yubin',
    version='0.2.0',
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
