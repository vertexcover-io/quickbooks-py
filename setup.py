#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

with open('requirements.txt') as reqfile:
    requirements = reqfile.readlines()

setup(
    name='quickbooks-py',
    version='0.0.3',
    description="QuickBooks Python Client is a python library for quickbooks api version 3",
    long_description=readme + '\n\n' + history,
    author="Ritesh Kadmawala",
    author_email='ritesh@loanzen.in',
    url='https://github.com/loanzen/quickbooks-py',
    packages=[
        'quickbook3',
    ],
    package_dir={'quicbook3':
                 'quickbook3'},
    include_package_data=True,
    install_requires=requirements,
    license="ISCL",
    zip_safe=False,
    keywords='quickbooks-py',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
)
