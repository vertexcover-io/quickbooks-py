# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
import json
import os
import sys
from test.test_support import EnvironmentVarGuard

from unittest import TestCase
from rauth import OAuth1Session
import rauth
import requests
from requests.structures import CaseInsensitiveDict
from quickbook3 import QuickBooks

try:
    from unittest import mock
except ImportError:
    import mock

from io import BytesIO


class BaseCase(TestCase):

    COMPANY_ID = 'company_id'
    CONSUMER_KEY = 'consumer_key'
    CONSUMER_SECRET = 'consumer_secret'
    ACCESS_TOKEN = 'access_token'
    ACCESS_SECRET = 'access_secret'

    CREDENTIAL_FILE = 'tests/fixtures/credfile'
    INCOMPLETE_CREDENTIAL_FILE = 'tests/fixtures/incomplete_credfile'

    PRODUCTION_URL = "https://quickbooks.api.intuit.com/v3"

    SANDBOX_URL = "https://sandbox-quickbooks.api.intuit.com/v3"

    def setUp(self):
        self.env = EnvironmentVarGuard()
        self.args = ()
        self.conf = {
            'header_auth': True,
            'headers': {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        }
        self.mock = mock.patch.object(rauth.OAuth1Session, 'request')
        self.request = self.mock.start()
        self.qbclient = None

    def tearDown(self):
        self.mock.stop()

    def set_default_client(self, qbclient=None):
        self.qbclient = qbclient or QuickBooks(company_id=self.COMPANY_ID,
                                               cred_file=self.CREDENTIAL_FILE)

        self.conf['realm'] = self.qbclient.company_id

    def response(self, resource, body=None, status_code=200, encoding='utf-8',
                 is_array=False, **headers):

        r = requests.Response()
        r.status_code = status_code
        r.encoding = encoding

        if body:
            r.json = lambda: body
        else:
            r.json = lambda: {resource: {}}

        r.headers = CaseInsensitiveDict({'Content-Type': 'application/json'})
        r.headers.update(headers)

        self.request.return_value = r

    def request_assertions(self, response):
        assert self.request.called is True
        assert isinstance(response, dict)
        conf = self.conf.copy()

        args, kwargs = self.request.call_args

        assert self.args == args

        for k in self.conf:
            assert k in kwargs
            assert self.conf[k] == kwargs[k]

        self.request.reset_mock()
        self.conf = conf

    def _get_url(self, resource, resource_id=None):
        if resource_id:
            return os.path.join(self.PRODUCTION_URL, 'company',
                                self.qbclient.company_id, resource, resource_id)
        else:
            return os.path.join(self.PRODUCTION_URL, 'company',
                                self.qbclient.company_id, resource)

    def delete(self, resource, resource_id=None):
        self.args = ('DELETE', self._get_url(resource, resource_id))

    def get(self, resource, resource_id=None):
        self.args = ('GET', self._get_url(resource, resource_id))

    def patch(self, resource, resource_id=None):
        self.args = ('PATCH', self._get_url(resource, resource_id))

    def post(self, resource, resource_id=None):
        self.args = ('POST', self._get_url(resource, resource_id))

    def put(self, resource, resource_id=None):
        self.args = ('PUT', self._get_url(resource, resource_id))


class RequestsBytesIO(BytesIO):
    def read(self, chunk_size, *args, **kwargs):
        return super(RequestsBytesIO, self).read(chunk_size)
