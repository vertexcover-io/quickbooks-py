# -*- coding: utf-8 -*-

"""
    A quickbooks client to access various quickbooks endpointz.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import os
import sys
import datetime
import traceback

from rauth import OAuth1Session

from .response import ResponseParser, QueryResponse, CDCResponse


try:
    import configparser
except ImportError:
    import ConfigParser as configparser

from .exceptions import *


def auth_required(func):
    def wrapper(self, *args, **kwargs):
        if all([self.consumer_key, self.consumer_secret,
                self.access_token, self.access_token_secret]):
            return func(self, *args, **kwargs)
        else:
            raise MissingCredentialsException()

    return wrapper


class QuickBooks(object):
    production_url = "https://quickbooks.api.intuit.com/v3"

    sandbox_url = "https://sandbox-quickbooks.api.intuit.com/v3"

    disconnect_url = "https://appcenter.intuit.com/api/v1/connection/disconnect"

    ACCOUNTING_SERVICES = ['account', 'attachable', 'bill', 'billpayment',
                           'class', 'companyinfo', 'creditmemo', 'customer',
                           'department', 'deposit', 'employee', 'estimate',
                           'invoice', 'item', 'journalentry', 'payment',
                           'paymentmethod', 'preferences', 'purchase',
                           'purchaseorder', 'salesreceipt', 'taxcode', 'taxrate',
                           'term', 'timeactivity', 'vendor', 'vendorcredit']

    CONSUMER_KEY_NAME = 'QB_CONSUMER_KEY'
    CONSUMER_SECRET_NAME = 'QB_CONSUMER_SECRET'
    ACCESS_TOKEN_NAME = 'QB_ACCESS_TOKEN'
    ACCESS_TOKEN_SECRET_NAME = 'QB_ACCESS_TOKEN_SECRET'

    def __init__(self, company_id, consumer_key=None, consumer_secret=None,
                 access_token=None, access_token_secret=None,
                 cred_file=None, sandbox_mode=False,
                 logger=None, peform_logging=False,
                 log_level=logging.ERROR):

        """
        :param company_id: This is the realmID obtained during authorization
        :type company_id: str
        :param consumer_key: Client consumer key, required for signing,
                             defaults to `None`.
        :type consumer_key: str
        :param consumer_secret: Client consumer secret, required for signing.
                                defaults to `None`.
        :type consumer_secret: str
        :param access_token: Access token, defaults to `None`.
        :type access_token: str
        :param access_token_secret: Access token secret, defaults to `None`.
        :type access_token_secret: str
        :param cred_file: Path to the credential file to read the consumer and
                          access token pair, defaults to `None`.

        :param sandbox_mode: A flag indicating whether to use production
            endpoints or sandbox endpoints, , defaults to `False`.
        :type sandbox_mode: bool
        :param logger: A logger to be used to log messages, error and debugging
            information
        :type logger: :class:`logging`

        :param peform_logging: A flag indicating whether to perform Logging,
            defaults to `True`.
        :type peform_logging: bool

        :param log_level: Mininum Log Level to log
        :type log_level: int
        :return:
        """

        self.sandbox_mode = sandbox_mode

        self.base_url_v3 = self.sandbox_url if self.sandbox_mode \
            else self.production_url

        self.company_id = company_id

        self.set_credentials(cred_file, consumer_key, consumer_secret,
                             access_token, access_token_secret)

        self.peform_logging = peform_logging

        self.logger = logger

        self.log_level = log_level

        if self.peform_logging and not self.logger:
            self.logger = logging.getLogger()
            self.logger.addHandler(logging.StreamHandler(sys.stdout))
            self.logger.setLevel(self.log_level)

        self._create_session()

    def create(self, resource, resource_dict, **params):
        url = self._get_crud_url(resource)
        response = self._execute(method='post', url=url,
                                 params=params or {},
                                 json=resource_dict)

        return response[resource]

    def read(self, resource, resource_id, **params):
        url = self._get_crud_url(resource, resource_id)
        response = self._execute(method='get', url=url, params=params or {})
        return response[resource]

    def update(self, resource, resource_dict, **params):
        url = self._get_crud_url(resource)
        response = self._execute(method='post', url=url,
                                 params=params or {},
                                 json=resource_dict)
        return response[resource]

    def delete(self, resource, resource_dict, **params):
        url = self._get_crud_url(resource)
        params = params or {}
        params['operation'] = 'delete'
        response = self._execute(method='post', url=url,
                                 params=params,
                                 json=resource_dict)

        return response[resource]

    def query(self, querybuilder, **params):
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

    def batch_query(self, querybuilder, **params):
        params = params or {}
        maxresults = querybuilder.get_maxresults()
        while True:
            query_response = self.query(querybuilder, **params)
            total_count = query_response.total_count
            startposition = query_response.startposition
            yield query_response
            if total_count < maxresults:
                return
            else:
                querybuilder.offset(startposition + maxresults)

    def report(self, name, **params):
        params = params or {}

        url = "/".join([self.base_url_v3, 'company', self.company_id,
                        'reports', name])

        response = self._execute(method='get', url=url, params=params)

        return response

    def cdc(self, entities, changed_since):
        if isinstance(changed_since, datetime.datetime):
            changed_since = changed_since.isoformat()

        params = {
            'entities': ','.join(entities),
            'changedSince': changed_since
        }

        url = "/".join([self.base_url_v3, 'company', self.company_id, 'cdc'])

        response = self._execute(method='get', url=url, params=params)

        return CDCResponse(entities, response['CDCResponse'])

    def disconnect(self):
        resp = self._execute(method='get', url=self.disconnect_url)
        if resp['ErrorCode'] > 0:
            raise DisconnectionError(resp['ErrorCode'], resp['ErrorMessage'])



    @auth_required
    def _execute(self, method, url, **kwargs):
        method = getattr(self.session, method)
        headers = {'Accept': 'application/json',
                   'Content-Type': 'application/json'}

        response = method(url, header_auth=True,
                          realm=self.company_id, headers=headers,
                          verify=False, **kwargs)
        return ResponseParser(response).parse()

    def _get_crud_url(self, resource, resource_id=None):
        resource = resource.lower()
        if not resource in self.ACCOUNTING_SERVICES:
            raise InvalidResourceError

        urlparts = [self.base_url_v3, 'company', self.company_id,
                    resource]

        if resource_id:
            urlparts.append(resource_id)

        return "/".join(urlparts)

    def _create_session(self):
        self.session = OAuth1Session(self.consumer_key,
                                     self.consumer_secret,
                                     self.access_token,
                                     self.access_token_secret)

    def set_credentials(self, cred_file, consumer_key, consumer_secret,
                        access_token, access_token_secret):

        if cred_file:
            self._read_creds_from_file(cred_file)
        else:
            try:
                self.consumer_key = consumer_key or os.environ[
                    self.CONSUMER_KEY_NAME]
                self.consumer_secret = consumer_secret or os.environ[
                    self.CONSUMER_SECRET_NAME]

                self.access_token = access_token or os.environ[
                    self.ACCESS_TOKEN_NAME]
                self.access_token_secret = access_token_secret or os.environ[
                    self.ACCESS_TOKEN_SECRET_NAME]

            except KeyError:
                raise MissingCredentialsException

    def _read_creds_from_file(self, filename):
        config = configparser.RawConfigParser()
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

        except configparser.NoOptionError, configparser.NoSectionError:
            raise MissingCredentialsException


