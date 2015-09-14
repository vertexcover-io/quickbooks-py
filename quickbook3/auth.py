# -*- coding: utf-8 -*-

"""
quickbook3.auth
~~~~~~~~~~~~~

This module contains a quickbook authentication service that implements the
OAuth 1.0/a auth flow using rauth.OAuth1Service
"""


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from rauth import OAuth1Service


class QuickBookAuthService(object):
    """
    A quickbook authentication service that is actually a wrapper around the
    :class:`~rauth.service.OAuth1Service` object. Primarily this wrapper is used
    to produce authenticated session objects.

    You can initialize :class:`QuickBookAuthService` as follows::

        service = QuickBookAuthService(consumer_key='123',
                                       consumer_secret='456',
                                       callback_url=http://example.com/authorize')

    where the callback_url is the redirect url where user is redirected by
    quicksbook once the user has authorized the application.

    Now the request token should be retrieved::

        request_token, request_token_secret = service.get_request_token_pair()

    This request token pair must be now saved in the user session. You then
    access the authorize URI and direct the client to authorize the requests
    on their behalf. This URI is retrieved as follows::

        authorize_url = service.get_authorize_url()

    Once the client has authorized the request, quickbook server redirects the
    user to callback_url specified during initialization. From the
    querystring of the callback url, we get the realmID(companyid), request token
    and the oauth_verifier. This request token can be verified against the one
    stored in the user session for securtiy purposes.

    You can now create a new instance of auth service by passing the consumer
    key pair as well as the request token pair obtained above::

        service = QuickBookAuthService(consumer_key='123',
                                       consumer_secret='456',
                                       request_token='789'
                                       request_token_secret='abc'
                                       callback_url=http://example.com/authorize')


    And obtain the access token pair as follows::

        access_token, access_token_secret = service.get_access_tokens()

    Using these, now you can access an authenticated session object as follows::

        session = OAuth1Session(consumer_key='123',
                                consumer_secret='456',
                                access_token='678',
                                access_token_secret='abc')


    Finally you have an authenticated session and are ready to make requests
    against Quickbooks api endpoints.

    """

    request_token_url = "https://oauth.intuit.com/oauth/v1/get_request_token"
    access_token_url = "https://oauth.intuit.com/oauth/v1/get_access_token"

    authorize_url = "https://appcenter.intuit.com/Connect/Begin"

    def __init__(self, consumer_key, consumer_secret,
                 callback_url, request_token=None, request_token_secret=None):

        """

        :param consumer_key: Client consumer key, required for signing.
        :type consumer_key: str
        :param consumer_secret: Client consumer secret, required for signing.
        :type consumer_secret: str
        :param callback_url: Redirect url where quickbook must redirect after
            authentication
        :type callback_url: str
        :param request_token: Request Token as returned by
            :class:`get_request_token_pair`.
        :type request_token: str
        :param request_token_secret: Request Token Secret as returned by
            :class:`get_request_token_pair`.
        :type request_token_secret: str

        """

        self.qbservice = OAuth1Service(name=None,
                                       consumer_key=consumer_key,
                                       consumer_secret=consumer_secret,
                                       request_token_url=self.request_token_url,
                                       access_token_url=self.access_token_url,
                                       authorize_url=self.authorize_url,
                                       base_url=None)

        self.callback_url = callback_url
        self.request_token = request_token
        self.request_token_secret = request_token_secret

    def get_request_token_pair(self):
        """
        Return a request token pair.
        """

        self.request_token, self.request_token_secret = \
            self.qbservice.get_request_token(
                params={'oauth_callback': self.callback_url})

        return self.request_token, self.request_token_secret

    def get_authorize_url(self):
        """
        Returns a formatted authorize URL.
        """

        if not self.request_token:
            self.get_request_token_pair()

        return self.qbservice.get_authorize_url(self.request_token)

    def get_access_tokens(self, oauth_verifier):
        """
        Returns an access token pair.

        :param oauth_verifier: A string returned by quickbooks server as
        querystring parameter and used to verify that request for access token is
        indeed coming from the application server.
        :type string:
        """

        return self.qbservice.get_access_token(
            self.request_token, self.request_token_secret,
            data={'oauth_verifier': oauth_verifier})

