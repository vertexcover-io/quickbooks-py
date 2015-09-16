# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from .exceptions import InvalidQueryError


class QueryBuilder(object):
    def __init__(self, entity):
        self.entity = entity
        self.columns = '*'
        self.filterflag = False
        self.filters = []
        self.incomplete_filter_flag = False
        self.countflag = False

        self.paginationflag = False
        self.maxresults = 100
        self.startposition = 1

    def get_entity(self):
        return self.entity

    def select(self, columns):
        if isinstance(columns, (tuple, list)):
            self.columns = ", ".join(columns)
        else:
            self.columns = columns
        return self

    def get_columns(self):
        return self.columns if self.columns else '*'

    def where(self, column):
        self._validate()
        self.incomplete_filter_flag = True
        self.filters.append(column)
        return self

    def equals(self, value):
        if value is None:
            value = ''

        column = self.filters[-1]
        if isinstance(value, bool):
            self.filters[-1] = "%s = %s" % (column, str(value).lower())

        else:
            self.filters[-1] = "%s = '%s'" % (column, value)

        self.incomplete_filter_flag = False
        return self

    def contains(self, values):
        if not isinstance(values, (list, tuple)):
            raise InvalidQueryError("Contains operator must "
                                    "receive a list/tuple of values")

        column = self.filters[-1]
        self.filters[-1] = "%s in %s" % (column, values)
        self.incomplete_filter_flag = False
        return self

    def gt(self, value):
        return self._operator('>', value)

    def gte(self, value):
        return self._operator('>=', value)

    def lt(self, value):
        return self._operator('<', value)

    def lte(self, value):
        return self._operator('<=', value)

    def _operator(self, op, value):
        try:
            float(value)
        except ValueError:
            raise InvalidQueryError("%s operator requires "
                                    "value of type integer/float" % op)

        column = self.filters[-1]
        self.filters[-1] = "%s %s '%s'" % (column, op, value)
        self.incomplete_filter_flag = False
        return self

    def like(self, value):
        if not isinstance(value, basestring):
            raise InvalidQueryError("Like operator requires "
                                    "value be of type string")

        column = self.filters[-1]
        self.filters[-1] = "%s Like '%s'" % (column, value)
        self.incomplete_filter_flag = False
        return self

    def set_filters(self, where):
        self.filters = where.split(' AND ')
        self._validate()

    def get_filters(self):
        return self.filters

    def count(self):
        self._validate()
        self.countflag = True
        self.columns = "count(*)"
        return self

    def is_count_query(self):
        return self.countflag

    def limit(self, maxresults):
        self._validate()
        self.paginationflag = True
        self.maxresults = maxresults
        return self

    def get_maxresults(self):
        return self.maxresults

    def offset(self, startposition):
        self._validate()
        self.paginationflag = True
        self.startposition = startposition
        return self

    def get_startposition(self):
        return self.startposition
    
    
    @classmethod
    def from_parts(cls, entity, columns='*', where=None, count=False, 
                   maxresults=100, startposition=0):
        
        qb = QueryBuilder(entity)
        qb.select(columns)
        qb.limit(maxresults)
        qb.offset(startposition)
        if count:
            qb.count()

        if where:
            qb.set_filters(where)

        return qb

    def build(self):
        self._validate()
        if not self.columns:
            self.columns = '*'

        query = "Select %s From %s" % (self.columns, self.entity)

        if self.filters:
            query += ' Where %s' % ' AND '.join(self.filters)

        if self.paginationflag:
            query += ' StartPosition %d MaxResults %d' % (self.startposition,
                                                          self.maxresults)

        return query

    def _validate(self):
        if self.incomplete_filter_flag:
            raise InvalidQueryError("Incomplete Filter Clause - > %s" %
                                    self.filters[-1])


