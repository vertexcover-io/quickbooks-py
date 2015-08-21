# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import json
import logging
import os
import sys
from rauth import OAuth1Session

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

from . import MissingCredentialsException


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
        url = self._get_url(resource)
        response = self._execute(method='post', url=url,
                                 params=params or {},
                                 json=resource_dict)

    def read(self, resource, resource_id, params=None):
        url = self._get_url(resource, resource_id)
        response = self._execute(method='get', url=url, params=params or {})

    def update(self, resource, resource_dict, params=None):
        url = self._get_url(resource)
        response = self._execute(method='post', url=url,
                                 params=params or {},
                                 json=resource_dict)

    def delete(self, resource, resource_dict, params=None):
        url = self._get_url(resource)
        params = params or {}
        params['operation'] = 'delete'
        response = self._execute(method='post', url=url,
                                 params=params,
                                 json=resource_dict)


    def query(self, querybuilder, params=None):
        pass

    def batch_query(self, querybuilder, limit=100):
        pass

    def _execute(self, method, url, **kwargs):
        method = getattr(self.session, method)
        headers = {'Accept': 'application/json',
                   'Content-Type': 'application/json'}
        response = method(url, header_auth=True,
                          realm=self.company_id, headers=headers,
                          **kwargs)

        print(response.status_code, response.text)

        return response

    def _get_url(self, resource, resource_id=None):
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



