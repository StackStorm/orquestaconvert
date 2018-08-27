from base_test_case import BaseActionTestCase

from orquestaconvert import expressions


class TestExpressions(BaseActionTestCase):
    __test__ = True

    def test_convert_expression(self):
        expr_dict = {"test": "value"}
        result = expressions.convert_expression(expr_dict)
        self.assertEquals(result, expr_dict)

    def test_convert_expression_string_jinja(self):
        expr = "{{ _.test }}"
        result = expressions.convert_expression_string(expr)
        self.assertEquals(result, "{{ ctx().test }}")

    def test_convert_expression_string_yaql(self):
        expr = "<% $.test %>"
        result = expressions.convert_expression_string(expr)
        self.assertEquals(result, "<% ctx().test %>")

    def test_convert_expression_string_other(self):
        expr = "test some raw string"
        result = expressions.convert_expression_string(expr)
        self.assertEquals(result, "test some raw string")
