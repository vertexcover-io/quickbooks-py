# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


class QuickBooksError(Exception):
    """
    A base exception for quickbooks-related errors
    """
    pass


class MissingCredentialsException(QuickBooksError):
    """
    Raised when either of credentials ie (consumer key, consumer secret,
    access token or access token secret) is missing
    """

    def __init__(self):
        super(MissingCredentialsException, self)\
            .__init__("All of consumer key, consumer secret "
                      "access token and access secret must be passed")


class InvalidQueryError(QuickBooksError):
    """
    Raised while constructing an invalid query using the querybuilder
    """
    pass


class HttpQuickBookError(QuickBooksError):
    """
    A base exception for http=related errors returned from quickbooks
    """
    pass


class AuthenticationError(HttpQuickBookError):
    """
    Raised when authentication to quickbook server fails.
    Corresponding to http status code 401
    """
    def __init__(self, *args):
        super(AuthenticationError, self).__init__('User authentication Failed')


class PermissionDenied(HttpQuickBookError):
    """
    Raised when the user doesn't have permission to access this resource.
    Corresponding to http status code 403
    """
    def __init__(self, *args):
        super(PermissionDenied, self).\
            __init__("User doesn't have permission to access this resource")


class NotFoundError(HttpQuickBookError):
    """
    Raised when the requested resource is not available.
    Corresponding to http status code 400
    """

    def __init__(self, *args):
        super(NotFoundError, self).__init__('Resource Not Found')


class ServerError(HttpQuickBookError):
    """
    Raised when there is some unknow error from the server.
    Corresponding to http status code 500
    """
    pass


class ServiceUnavailable(HttpQuickBookError):
    """
    Raised when server is down or not available.
    Corresponding to http status code 503
    """
    def __init__(self, *args):
        super(ServiceUnavailable, self).__init__('Service Unavailable')


class UnknownError(HttpQuickBookError):
    """
    Raised corresponding to all other http error codes
    """

    def __init__(self, status_code, error):
        super(UnknownError, self).__init__(
            "Status Code: %d. Reason: %s" % (status_code, error))


class GenericError(HttpQuickBookError):
    """
    A base exception for quickbook specific error which is denoted by Fault.
    """

    def __init__(self, errors):
        self.errors = errors
        error_message = 'Validation Error:'
        for error in self.errors:
            error_message += ' %s.' % error['Detail']

        super(HttpQuickBookError, self).__init__(error_message)


class ValidationFault(GenericError):
    """
    Raised when some invalid data have been sent.
    """
    pass


class ServiceError(GenericError):
    """
    A non-recoverable error. Something failed on the server
    """
    pass
