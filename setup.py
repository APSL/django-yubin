#!/usr/bin/env python3

from setuptools import setup


INSTALL_REQUIRES = [
    'celery>=5.0,<6',
    'mail-parser',
    'pytz',
]


with open('README.rst') as docs_index:
    long_description = docs_index.read()


def get_version():
    version_globals = {}
    with open('django_yubin/version.py') as f:
        exec(f.read(), version_globals)
    return version_globals['__version__']


setup(
    name='django-yubin',
    version=get_version(),
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
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.0',
        'Framework :: Django :: 4.1',
        'Framework :: Django :: 4.2',
    ]
)
