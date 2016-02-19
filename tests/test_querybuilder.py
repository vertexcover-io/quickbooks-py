# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from quickbook3 import QueryBuilder, InvalidQueryError
from tests.utils import BaseCase


class TestQueryBuilder(BaseCase):

    def test_get_entity(self):
        qb = QueryBuilder('company')
        entity = qb.get_entity()
        self.assertEqual(entity, 'company')

    def test_select_chainable(self):
        qb = QueryBuilder('company')
        ret = qb.select("a, b")
        self.assertEqual(qb, ret)

    def test_select_columns_list(self):
        qb = QueryBuilder('company')
        columns = ['a', 'b']
        columns_str = ", ".join(columns)
        qb.select(columns)
        self.assertEqual(qb.columns, columns_str)

    def test_select_columns_tuple(self):
        qb = QueryBuilder('company')
        columns = ('a', 'b')
        columns_str = ", ".join(columns)
        qb.select(columns)
        self.assertEqual(qb.columns, columns_str)

    def test_select_columns_str(self):
        qb = QueryBuilder('company')
        columns = 'a,b'
        qb.select(columns)
        self.assertEqual(qb.columns, columns)

    def test_get_columns_all(self):
        qb = QueryBuilder('company')
        self.assertEqual(qb.get_columns(), '*')

    def test_get_columns_specified(self):
        qb = QueryBuilder('company')
        columns = 'a, b'
        qb.select(columns)
        self.assertEqual(qb.get_columns(), columns)

    def test_where_chainable(self):
        self._test_clause_chainable("where", "a", where=False)

    def test_where_clause(self):
        qb = QueryBuilder('company')
        qb.where("a")
        self.assertEqual(qb.incomplete_filter_flag, True)
        self.assertEqual(len(qb.filters), 1)
        self.assertEqual(qb.filters[0], 'a')

    def test_incomplete_where_clause_raises_error(self):
        qb = QueryBuilder('company')
        qb.where("a")
        self.assertRaisesRegexp(InvalidQueryError,
                                r'Incomplete Filter Clause', qb.build)

    def test_equal_clause_raise_error_without_where(self):
        qb = QueryBuilder('company')
        self.assertRaisesRegexp(InvalidQueryError,
                                r'preceeded by where',
                                qb.equals, 'a')

    def test_equal_clause_chainable(self):
        self._test_clause_chainable("equals", "5")

    def test_equal_clause_bool(self):
        qb = QueryBuilder('company')
        qb.where("a").equals(True)
        self._test_clause(qb, "a", '=', "true")

    def test_equal_clause_none(self):
        qb = QueryBuilder('company')
        qb.where("a").equals(None)
        self._test_clause(qb, "a", '=', "''")

    def test_equal_clause(self):
        qb = QueryBuilder('company')
        qb.where("a").equals("b")
        self._test_clause(qb, "a", '=', "'b'")

    def test_contains_clause_list(self):
        qb = QueryBuilder('company')
        values = [1, 2, 3]
        qb.where('a').contains(values)
        self._test_clause(qb, "a", 'in', str(values))

    def test_contains_clause_tuple(self):
        qb = QueryBuilder('company')
        values = (1, 2, 3)
        qb.where('a').contains(values)
        self._test_clause(qb, "a", 'in', str(values))

    def test_contains_clause_raises_exception_str_value(self):
        qb = QueryBuilder('company')
        values = "fgf"
        qb = qb.where('a')
        self.assertRaisesRegexp(InvalidQueryError, "list/tuple of values",
                                qb.contains, values)

    def test_gt_clause(self):
        qb = QueryBuilder('company')
        qb.where("a").gt("5")
        self._test_clause(qb, "a", ">", "'5'")
        
    def test_gt_chainable(self):
        return self._test_clause_chainable("gt", "5")

    def test_gte_clause(self):
        qb = QueryBuilder('company')
        qb.where("a").gte("5")
        self._test_clause(qb, "a", ">=", "'5'")
        
    def test_gte_chainable(self):
        return self._test_clause_chainable("gte", "5")
        
    def test_lt_clause(self):
        qb = QueryBuilder('company')
        qb.where("a").lt("5")
        self._test_clause(qb, "a", "<", "'5'")
        
    def test_lt_chainable(self):
        return self._test_clause_chainable("lt", "5")        

    def test_lte_clause(self):
        qb = QueryBuilder('company')
        qb.where("a").lte("5")
        self._test_clause(qb, "a", "<=", "'5'")
        
    def test_lte_chainable(self):
        return self._test_clause_chainable("lte", "5")

    def test_like_clause(self):
        qb = QueryBuilder('company')
        qb.where("a").like("5")
        self._test_clause(qb, "a", "Like", "'5'")

    def test_like_clause_raise_error_on_non_str(self):
        qb = QueryBuilder('company')
        qb.where("a")
        self.assertRaisesRegexp(InvalidQueryError, r"value be of type string",
                                qb.like, True)

    def test_like_chainable(self):
        return self._test_clause_chainable("like", "5")

    def _test_clause_chainable(self, clause, param, where=True):
        qb = QueryBuilder('company')
        if where:
            qb.where("a")
        ret = getattr(qb, clause)(param)
        self.assertEqual(qb, ret)

    def _test_clause(self, qb, lhs, op, rhs):
        self.assertEqual(qb.incomplete_filter_flag, False)
        self.assertEqual(qb.filters[0], "{} {} {}".format(lhs, op, rhs))


