# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division

import requests
import xmltodict

from .exceptions import AuthenticationError, PermissionDenied, NotFoundError, \
    ServerError, ServiceUnavailable, ValidationFault, UnknownError


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
        'SERVICEFAULT': ServerError,
        'SYSTEMFAULT': ServerError
    }

    def __init__(self, response):
        super(ResponseParser, self).__init__()
        self.response = response

    def parse(self):
        status_code = self.response.status_code
        if status_code != requests.codes.ok:
            self.parse_http_error()

        elif self.is_xml_response():
            self.parse_quickbooks_error()

        else:
            json_response = self.response.json()
            if 'Fault' in json_response:
                self.parse_quickbooks_error()
            else:
                return json_response

    def parse_http_error(self):
        status_code = self.response.status_code
        if status_code in self.HTTP_CODE_EXCEPTION_MAP:
            exception = self.HTTP_CODE_EXCEPTION_MAP[status_code]

            raise exception(self.response.reason)

        elif status_code == requests.codes.bad_request:
            return self.parse_quickbooks_error()
        else:
            raise UnknownError(status_code, self.response.reason)

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


class QueryResponse(object):

    def __init__(self, entity, query_response):
        self.entity = entity
        self.object_list = query_response.get(entity, [])
        self.startposition = query_response.get('startPosition', 1)
        self.maxresults = query_response['maxResults']
        self.total_count = query_response.get('totalCount', self.maxresults)

    def __repr__(self):
        return "Entity: %s, StartPosition: %d, Count: %d, " \
               "MaxResults: %d" % (self.entity, self.startposition,
                                   self.total_count, self.maxresults)


class CDCResponse(object):
    def __init__(self, entities, cdc_response):
        if isinstance(cdc_response, (list, tuple)):
            cdc_response = cdc_response[0]

        self.upsert = {}
        self.delete = {}

        for ind, entity in enumerate(entities):
            self.delete[entity] = []
            self.upsert[entity] = []

            query_response = cdc_response['QueryResponse'][ind]
            for obj in query_response.get(entity, []):
                if not 'status' in obj:
                    self.upsert[entity].append(obj)
                else:
                    self.delete[entity].append(obj)
                    
    def __repr__(self):
        upsert = "Upsert: %s"  % \
                 (str({entity: len(self.upsert[entity])
                       for entity in self.upsert.keys()}))
        
        delete = "Delete: %s"  % \
                 (str({entity: len(self.delete[entity])
                       for entity in self.delete.keys()}))
        
        return "%s, %s" % (upsert, delete)