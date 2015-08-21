# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from rauth import OAuth1Service


class QuickBookAuthService(object):

    request_token_url = "https://oauth.intuit.com/oauth/v1/get_request_token"
    access_token_url = "https://oauth.intuit.com/oauth/v1/get_access_token"

    authorize_url = "https://appcenter.intuit.com/Connect/Begin"

    def __init__(self, consumer_key, consumer_secret,
                 callback_url, request_token=None, request_token_secret=None):
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
        self.request_token, self.request_token_secret = \
            self.qbservice.get_request_token(
                params={'oauth_callback': self.callback_url})

        return self.request_token, self.request_token_secret

    def get_authorize_url(self):
        if not self.request_token:
            self.get_request_token_pair()

        return self.qbservice.get_authorize_url(self.request_token)

    def get_access_tokens(self, oauth_verifier):
        return self.qbservice.get_access_token(
            self.request_token, self.request_token_secret,
            data={'oauth_verifier': oauth_verifier})

