# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


class MissingCredentialsException(Exception):
    def __init__(self, *args, **kwargs):
        super("All of consumer key, consumer secret, access key and "
              "access secret must be passed")


class InvalidQueryError(SyntaxError):
    pass