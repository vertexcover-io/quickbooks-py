# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
import logging
from quickbook3 import QuickBooks, MissingCredentialsException, \
    InvalidResourceError
from tests.utils import BaseCase


class TestQuickbooks(BaseCase):

    def test_init(self):
        self.set_default_client(QuickBooks(company_id=self.COMPANY_ID,
                                           consumer_key=self.CONSUMER_KEY,
                                           consumer_secret=self.CONSUMER_SECRET,
                                           access_token=self.ACCESS_TOKEN,
                                           access_token_secret=self.ACCESS_SECRET))

        self.assertEqual(self.qbclient.company_id, self.COMPANY_ID)
        self._assert_credentials()
        self.assertEqual(self.qbclient.sandbox_mode, False)
        self.assertIsNone(self.qbclient.logger)
        self.assertEqual(self.qbclient.log_level, logging.ERROR)

    def test_missing_consumer_key_exception(self):
        self.assertRaises(MissingCredentialsException,
                          QuickBooks,
                          company_id=self.COMPANY_ID,
                          consumer_secret=self.CONSUMER_SECRET,
                          access_token=self.ACCESS_TOKEN,
                          access_token_secret=self.ACCESS_SECRET)

    def test_missing_access_token_secret_exception(self):
        self.assertRaises(MissingCredentialsException,
                          QuickBooks,
                          company_id=self.COMPANY_ID,
                          consumer_key=self.CONSUMER_KEY,
                          consumer_secret=self.CONSUMER_SECRET,
                          access_token=self.ACCESS_TOKEN)

    def test_read_creds_from_file(self):
        self.set_default_client(QuickBooks(company_id=self.COMPANY_ID,
                                           cred_file=self.CREDENTIAL_FILE))
        self._assert_credentials()

    def test_exception_read_incomplete_creds(self):
        self.assertRaises(MissingCredentialsException,
                          QuickBooks,
                          company_id=self.COMPANY_ID,
                          cred_file=self.INCOMPLETE_CREDENTIAL_FILE)

    def test_credentials_from_environment(self):
        self.env.set('QB_CONSUMER_KEY', self.CONSUMER_KEY)
        self.env.set('QB_CONSUMER_SECRET', self.CONSUMER_SECRET)
        self.env.set('QB_ACCESS_TOKEN', self.ACCESS_TOKEN)
        self.env.set('QB_ACCESS_TOKEN_SECRET', self.ACCESS_SECRET)

        with self.env:
            self.set_default_client(QuickBooks(company_id=self.COMPANY_ID))
            self._assert_credentials()

    def _assert_credentials(self):
        self.assertEqual(self.qbclient.consumer_key, self.CONSUMER_KEY)
        self.assertEqual(self.qbclient.consumer_secret, self.CONSUMER_SECRET)
        self.assertEqual(self.qbclient.access_token, self.ACCESS_TOKEN)
        self.assertEqual(self.qbclient.access_token_secret, self.ACCESS_SECRET)

    def test_base_url_sandbox(self):
        self.set_default_client(QuickBooks(company_id=self.COMPANY_ID,
                                           sandbox_mode=True,
                                           cred_file=self.CREDENTIAL_FILE))

        self.assertEqual(self.qbclient.base_url_v3, self.SANDBOX_URL)

    def test_base_url_production(self):
        self.set_default_client()
        self.assertEqual(self.qbclient.base_url_v3, self.PRODUCTION_URL)

    def test_crud_url_list(self):
        self.set_default_client()
        customer_url = self.PRODUCTION_URL + '/company/' + self.COMPANY_ID + '/customer'
        self.assertEqual(self.qbclient._get_crud_url('customer'), customer_url)

    def test_crud_url_detail(self):
        self.set_default_client()
        customer_id = 'customer_id'
        customer_url = self.PRODUCTION_URL + '/company/' + self.COMPANY_ID + '/customer/' + customer_id
        self.assertEqual(self.qbclient._get_crud_url('customer', customer_id), customer_url)

    def test_invalid_resource(self):
        self.set_default_client()
        self.assertRaises(InvalidResourceError, self.qbclient._get_crud_url, 'invalid')

    def test_create_resource(self):
        resource_dict = {'customer': {'name': 'Name'}}
        self.set_default_client()
        self.response('customer')
        self.post('customer')
        self.conf['json'] = resource_dict
        resp = self.qbclient.create('customer', resource_dict)
        self.request_assertions(resp)

    def test_read_resource(self):
        resource_id = 'customer_id'
        self.set_default_client()
        self.response('customer')
        self.get('customer', resource_id)

        resp = self.qbclient.read('customer', resource_id)
        self.request_assertions(resp)

    def test_update_resource(self):
        resource_dict = {'customer': {'name': 'Name'}}
        self.set_default_client()
        self.response('customer')
        self.post('customer')
        self.conf['json'] = resource_dict
        resp = self.qbclient.update('customer', resource_dict)
        self.request_assertions(resp)

    def test_delete_resource(self):
        resource_dict = {'customer': {'name': 'Name'}}
        self.set_default_client()
        self.response('customer')
        self.post('customer')
        self.conf['json'] = resource_dict
        self.conf['params'] = {'operation': 'delete'}
        resp = self.qbclient.delete('customer', resource_dict)
        self.request_assertions(resp)


