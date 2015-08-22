# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import os
import sys

from rauth import OAuth1Session
import requests
import xmltodict


try:
    import configparser
except ImportError:
    import ConfigParser as configparser

from .exceptions import *
from .querybuilder import *


class QuickBooks(object):
    production_url = "https://quickbooks.api.intuit.com/v3"

    sandbox_url = "https://sandbox-quickbooks.api.intuit.com/v3"

    ACCOUNTING_SERVICES = [
        "Account", "Attachable", "Bill", "BillPayment",
        "Class", "CompanyInfo", "CreditMemo", "Customer",
        "Department",
        "Deposit",
        "Employee", "Estimate", "Invoice",
        "Item", "JournalEntry", "Payment", "PaymentMethod",
        "Preferences", "Purchase", "PurchaseOrder",
        "SalesReceipt", "TaxCode", "TaxRate", "Term",
        "TimeActivity", "Vendor", "VendorCredit"
    ]

    CONSUMER_KEY_NAME = 'QB_CONSUMER_KEY'
    CONSUMER_SECRET_NAME = 'QB_CONSUMER_SECRET'
    ACCESS_TOKEN_NAME = 'QB_ACCESS_TOKEN'
    ACCESS_TOKEN_SECRET_NAME = 'QB_ACCESS_TOKEN_SECRET'

    def __init__(self, company_id, consumer_key=None, consumer_secret=None,
                 access_token=None, access_token_secret=None,
                 cred_file=None, sandbox_mode=False,
                 logger=None, peform_logging=False,
                 log_level=logging.ERROR):

        self.sandbox_mode = sandbox_mode

        self.base_url_v3 = self.sandbox_url if self.sandbox_mode \
            else self.production_url

        self.company_id = company_id

        if cred_file:
            self._read_creds_from_file(cred_file)

        else:
            self._get_credentials(consumer_key, consumer_secret,
                                  access_token, access_token_secret)

        self.peform_logging = peform_logging

        self.logger = logger

        self.log_level = log_level

        if self.peform_logging and not self.logger:
            self.logger = logging.getLogger()
            self.logger.addHandler(logging.StreamHandler(sys.stdout))
            self.logger.setLevel(self.log_level)

        self._create_session()

    def create(self, resource, resource_dict, params=None):
        url = self._get_crud_url(resource)
        response = self._execute(method='post', url=url,
                                 params=params or {},
                                 json=resource_dict)

        return response[resource]

    def read(self, resource, resource_id, params=None):
        url = self._get_crud_url(resource, resource_id)
        response = self._execute(method='get', url=url, params=params or {})
        return response[resource]

    def update(self, resource, resource_dict, params=None):
        url = self._get_crud_url(resource)
        response = self._execute(method='post', url=url,
                                 params=params or {},
                                 json=resource_dict)
        return response[resource]

    def delete(self, resource, resource_dict, params=None):
        url = self._get_crud_url(resource)
        params = params or {}
        params['operation'] = 'delete'
        response = self._execute(method='post', url=url,
                                 params=params,
                                 json=resource_dict)

        return response[resource]

    def query(self, querybuilder, params=None):
        query = querybuilder.build()
        entity = querybuilder.get_entity()
        count = querybuilder.is_count_query()
        return self._query(entity, query, count, params)

    def _query(self, entity, query, count=False, params=None):
        params = params or {}

        params['query'] = query

        url = "/".join([self.base_url_v3, 'company', self.company_id, 'query'])

        response = self._execute(method='get', url=url, params=params)

        if count:
            return response['QueryResponse']['totalCount']
        else:
            return QueryResponse(entity, response['QueryResponse'])

    def batch_query(self, querybuilder, params=None):
        params = params or {}
        while True:
            query_response = self.query(querybuilder, params)
            total_count = query_response.total_count
            startposition = query_response.startposition
            maxresults = query_response.maxresults
            yield query_response
            if total_count < maxresults:
                return
            else:
                querybuilder.offset(startposition + maxresults)

    def report(self, name, params=None):
        params = params or {}

        url = "/".join([self.base_url_v3, 'company', self.company_id,
                        'reports', name])

        response = self._execute(method='get', url=url, params=params)

        return response

    def _execute(self, method, url, **kwargs):
        method = getattr(self.session, method)
        headers = {'Accept': 'application/json',
                   'Content-Type': 'application/json'}

        response = method(url, header_auth=True,
                          realm=self.company_id, headers=headers,
                          **kwargs)

        return ResponseParser(response).parse()

    def _get_crud_url(self, resource, resource_id=None):
        urlparts = [self.base_url_v3, 'company', self.company_id,
                    resource.lower()]

        if resource_id:
            urlparts.append(resource_id)

        return "/".join(urlparts)

    def _create_session(self):
        self.session = OAuth1Session(self.consumer_key,
                                     self.consumer_secret,
                                     self.access_token,
                                     self.access_token_secret)

    def _get_credentials(self, consumer_key, consumer_secret, access_token,
                         access_token_secret):

        try:
            self.consumer_key = consumer_key or \
                                os.environ[self.CONSUMER_KEY_NAME]
            self.consumer_secret = consumer_secret or \
                                   os.environ[self.CONSUMER_SECRET_NAME]

            self.access_token = access_token or \
                                os.environ[self.ACCESS_TOKEN_NAME]
            self.access_token_secret = access_token_secret or \
                                       os.environ[self.ACCESS_TOKEN_SECRET_NAME]

        except KeyError:
            raise MissingCredentialsException

    def _read_creds_from_file(self, filename):
        config = configparser.ConfigParser()
        config.read(filename)

        try:
            self.consumer_key = config.get('credentials',
                                           self.CONSUMER_KEY_NAME)
            self.consumer_secret = config.get('credentials',
                                              self.CONSUMER_SECRET_NAME)

            self.access_token = config.get('credentials',
                                           self.ACCESS_TOKEN_NAME)
            self.access_token_secret = config.get('credentials',
                                                  self.ACCESS_TOKEN_SECRET_NAME)

        except configparser.NoOptionError:
            raise MissingCredentialsException


class ResponseParser(object):

    HTTP_CODE_EXCEPTION_MAP = {
        401: AuthenticationError,
        403: PermissionDenied,
        404: NotFoundError,
        500: ServerError,
        503: ServiceUnavailable
    }

    FAULT_TYPE_EXCEPTION_MAP = {
        'AUTHENTICATION': AuthenticationError,
        'AUTHORIZATION': PermissionDenied,
        'VALIDATIONFAULT': ValidationFault,
        'SERVICEFAULT': ServerError
    }

    def __init__(self, response):
        super(ResponseParser, self).__init__()
        self.response = response

    def parse(self):
        status_code = self.response.status_code
        if status_code != requests.codes.ok:
            self.response.parse_http_error()

        elif self.is_xml_response():
            self.parse_quickbooks_error()

        else:
            json_response = self.response.json()
            if 'Fault' in json_response:
                self.parse_quickbooks_error()
            else:
                return json_response

    def parse_http_error(self, response):
        status_code = response.status_code
        if status_code in self.HTTP_CODE_EXCEPTION_MAP:
            exception = self.HTTP_CODE_EXCEPTION_MAP[status_code]

            raise exception(response.reason)

        elif status_code == requests.codes.bad_request:
            return self.parse_quickbooks_error()
        else:
            raise UnknownError(status_code, response.reason)

    def parse_quickbooks_error(self):
        if self.is_xml_response():
            parsed_error = xmltodict.parse(self.response.json)
            fault = parsed_error['IntuitResponse']['Fault']
            fault_type = fault['@type'].upper()
            for error in fault['Errors']:
                error['code'] = error['@code']
                del error['@code']

        else:
            fault = self.response.json()['Fault']
            fault_type = fault['type'].upper()

        raise self.FAULT_TYPE_EXCEPTION_MAP[fault_type](fault['Error'])

    def is_xml_response(self):
        return 'xml' in self.response.headers['content-type']

