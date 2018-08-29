from base_test_case import BaseActionTestCase

from orquestaconvert.expressions.base import BaseExpressionConverter


class TestExpressionsBase(BaseActionTestCase):
    __test__ = True

    def test_wrap_expression_raises(self):
        with self.assertRaises(NotImplementedError):
            BaseExpressionConverter.wrap_expression('junk')

    def test_unwrap_expression_raises(self):
        with self.assertRaises(NotImplementedError):
            BaseExpressionConverter.unwrap_expression('junk')

    def test_convert_string_raises(self):
        with self.assertRaises(NotImplementedError):
            BaseExpressionConverter.convert_string('junk')
