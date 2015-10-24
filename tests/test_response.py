# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from unittest import TestCase
import requests
from quickbook3 import *

try:
    from unittest import mock
except ImportError:
    import mock


ERROR_MSG_MAP = {
    AuthenticationError: 'User authentication Failed',
    PermissionDenied: 'permission',
    NotFoundError: 'Not Found',
    ServiceUnavailable: 'Service Unavailable',
    ServerError: 'Server Error'
}

class TestResponseParser(TestCase):

    def create_response_parser(self, status_code=200, response_body=None,
                               content_type='application/json', **kwargs):

        resp = requests.Response()
        resp.status_code = status_code
        response_body = response_body or {}
        resp.json = lambda: response_body
        for key, val in kwargs.items():
            setattr(resp, key, val)

        if content_type:
            resp.headers['content-type'] = content_type

        return ResponseParser(resp)

    def test_parse_response_success(self):
        body = {'response': 'success'}
        parser = self.create_response_parser(200, body)
        self.assertEqual(body, parser.parse())

    def test_is_xml_response_success(self):
        parser = self.create_response_parser(content_type='application/xml')
        assert parser.is_xml_response()

    def test_is_xml_response_failure(self):
        parser = self.create_response_parser()
        assert not parser.is_xml_response()

    def _test_http_exception(self, status_code, exception_type,
                             reason=None,
                             assert_status=False):

        reason = reason or ERROR_MSG_MAP[exception_type]
        parser = self.create_response_parser(status_code=status_code, reason=reason)
        with self.assertRaises(exception_type) as cm:
            parser.parse()

        err = str(cm.exception)

        if assert_status:
            assert str(status_code) in err

        assert reason.lower() in err.lower()

    def test_parse_response_unknown_error(self):
        self._test_http_exception(409, UnknownError, 'Conflict')

    def test_parse_response_authentication_error(self):
        self._test_http_exception(401, AuthenticationError)

    def test_parse_response_authorization_error(self):
        self._test_http_exception(403, PermissionDenied)

    def test_parse_response_notfound_error(self):
        self._test_http_exception(404, NotFoundError)

    def test_parse_response_server_error(self):
        self._test_http_exception(500, ServerError)

    def test_parse_response_service_unavailable(self):
        self._test_http_exception(503, ServiceUnavailable)

    def _test_bad_request_error(self, fault_type, exception_type, reason=None):
        reason = reason or ERROR_MSG_MAP[exception_type]
        parser = self.create_response_parser(status_code=400,
                                             response_body={
                                                 'Fault': {
                                                     'type': fault_type,
                                                     'Error': reason
                                                 }
                                             })

        with self.assertRaises(exception_type) as cm:
            parser.parse()

        err = str(cm.exception)
        assert reason.lower() in err.lower()

    def test_bad_request_authentication_error(self):
        self._test_bad_request_error('authentication', AuthenticationError)

    def test_bad_request_authorization_error(self):
        self._test_bad_request_error('authorization', PermissionDenied)

    def test_bad_request_service_fault(self):
        self._test_bad_request_error('SERVICEFAULT', ServerError)

    def test_bad_request_system_fault(self):
        self._test_bad_request_error('SYSTEMFAULT', ServerError)

    def test_bad_request_validation_error(self):
        errors = [
            {
                'Detail': 'First Error'
            },
            {
                'Detail': 'Second Error'
            }
        ]
        parser = self.create_response_parser(status_code=400,
                                             response_body={
                                                 'Fault': {
                                                     'type': 'validationfault',
                                                     'Error': errors
                                                 }
                                             })

        with self.assertRaises(ValidationFault) as cm:
            parser.parse()

        err_msg = str(cm.exception)

        for err in errors:
            assert err['Detail'] in err_msg

