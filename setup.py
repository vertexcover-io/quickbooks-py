# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from setuptools import setup, find_packages


with open('requirements.txt') as f:
    required = f.read().splitlines()



setup(
    name='quickbooks',
    version='0.1',
    author='Ritesh Kadmawala',
    author_email='ritesh@loanzen.in',
    description='A simple python client for the Quickbooks API Version 3.',
    url='https://github.com/loanzen/quickbooks-py',
    license='MIT',

    install_requires=required,

    packages=find_packages(),
)