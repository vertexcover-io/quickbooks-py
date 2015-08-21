# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division


class QueryBuilder(object):
    def __init__(self, entity):
        self.entity = entity

        self.columns = '*'

        self.selectflag = False

        self.filterflag = False
        self.filters = []
        self.incomplete_filter_flag = False

        self.paginationflag = False
        self.maxresult = 1000
        self.startposition = 1

    def select(self, columns=None):
        if self.selectflag:
            raise InvalidQueryError("Multiple select clauses are not allowed")

        self.selectflag = True
        if columns:
            self.columns = columns.split(", ")

        return self

    def _validate(self, filter_op=True):
        if not self.selectflag:
            raise InvalidQueryError("Must be preceded by a select clause")

        if not filter_op and self.incomplete_filter_flag:
            raise InvalidQueryError("Incomplete Filter Clause - > %s" %
                                    self.filters[-1])

    def where(self, column):
        self._validate(filter_op=False)
        self.incomplete_filter_flag = True
        self.filters.append(column)
        return self

    def equals(self, value):
        self._validate()
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
        self._validate()
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
        self._validate()
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
        self._validate()
        if not isinstance(value, basestring):
            raise InvalidQueryError("Like operator requires "
                                    "value be of type string")

        column = self.filters[-1]
        self.filters[-1] = "%s Like '%s'" % (column, value)
        self.incomplete_filter_flag = False
        return self

    def count(self):
        self._validate(filter_op=False)
        self.columns = "count(*)"
        return self

    def limit(self, maxresults):
        self._validate(filter_op=False)
        self.paginationflag = True
        self.maxresult = maxresults
        return self

    def offset(self, startposition):
        self._validate(filter_op=False)
        self.paginationflag = True
        self.startposition = startposition
        return self

    def build(self):
        self._validate(filter_op=False)
        query = "Select %s From %s" % (self.columns, self.entity)

        if self.filters:
            query += ' Where %s' % ' AND '.join(self.filters)

        if self.paginationflag:
            query += ' StartPosition %d MaxResults %d' % (self.startposition,
                                                          self.maxresult)

        return query

