from base_test_case import BaseActionTestCase

from orquestaconvert import expressions


class TestExpressions(BaseActionTestCase):
    __test__ = True

    def test_convert_expression(self):
        expr_dict = {"test": "value"}
        result = expressions.convert_expression(expr_dict)
        self.assertEquals(result, expr_dict)
