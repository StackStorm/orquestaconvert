from tests.base_test_case import BaseTestCase

from orquestaconvert.expressions.base import (
    AbstractBaseExpressionConverter,
    BaseExpressionConverter,
)


class AbstractBaseExpressionsTestCase(BaseTestCase):
    __test__ = True

    def test_wrap_expression_raises(self):
        with self.assertRaises(NotImplementedError):
            AbstractBaseExpressionConverter.wrap_expression('junk')

    def test_unwrap_expression_raises(self):
        with self.assertRaises(NotImplementedError):
            AbstractBaseExpressionConverter.unwrap_expression('junk')

    def test_convert_string_raises(self):
        with self.assertRaises(NotImplementedError):
            AbstractBaseExpressionConverter.convert_string('junk')

    def test_convert_context_vars_raises(self):
        with self.assertRaises(NotImplementedError):
            AbstractBaseExpressionConverter.convert_context_vars('junk')

    def test_convert_task_result_raises(self):
        with self.assertRaises(NotImplementedError):
            AbstractBaseExpressionConverter.convert_task_result('junk')

    def test_convert_st2kv(self):
        with self.assertRaises(NotImplementedError):
            AbstractBaseExpressionConverter.convert_st2kv('junk')


class BaseExpressionsTestCase(BaseTestCase):
    __test__ = True

    def test_wrap_expression_raises(self):
        with self.assertRaises(NotImplementedError):
            BaseExpressionConverter.wrap_expression('junk')

    def test_unwrap_expression_raises(self):
        with self.assertRaises(NotImplementedError):
            BaseExpressionConverter.unwrap_expression('junk')

    def test_convert_static_string(self):
        with self.assertRaises(NotImplementedError):
            BaseExpressionConverter.convert_string('junk')

    def test_convert_static_context_vars_raises(self):
        with self.assertRaises(NotImplementedError):
            BaseExpressionConverter.convert_context_vars('junk')
