from base_test_case import BaseActionTestCase

from orquestaconvert.expressions import ExpressionConverter


class TestExpressions(BaseActionTestCase):
    __test__ = True

    def test_convert_expression(self):
        expr_dict = {"test": "value"}
        result = ExpressionConverter.convert(expr_dict)
        self.assertEquals(result, expr_dict)

    def test_convert_expression_dict(self):
        expr = {
            "jinja_str": "{{ _.test_jinja }}",
            "yaql_str": "<% $.test_yaql %>",
        }
        result = ExpressionConverter.convert_dict(expr)
        self.assertEquals(result, {
            "jinja_str": "{{ ctx().test_jinja }}",
            "yaql_str": "<% ctx().test_yaql %>",
        })

    def test_convert_expression_dict_nested_list(self):
        expr = {
            "expr_list":
            [
                "{{ _.a }}",
                "<% $.a %>",
            ]
        }
        result = ExpressionConverter.convert_dict(expr)
        self.assertEquals(result, {
            "expr_list":
            [
                "{{ ctx().a }}",
                "<% ctx().a %>",
            ]
        })

    def test_convert_expression_dict_nested_dict(self):
        expr = {
            "expr_dict":
            {
                "nested_jinja": "{{ _.a }}",
                "nested_yaql": "<% $.a %>",
            }
        }
        result = ExpressionConverter.convert_dict(expr)
        self.assertEquals(result, {
            "expr_dict":
            {
                "nested_jinja": "{{ ctx().a }}",
                "nested_yaql": "<% ctx().a %>",
            }
        })

    def test_convert_expression_list(self):
        expr = [
            "{{ _.test_jinja }}",
            "<% $.test_yaql %>",
        ]
        result = ExpressionConverter.convert_list(expr)
        self.assertEquals(result, [
            "{{ ctx().test_jinja }}",
            "<% ctx().test_yaql %>",
        ])

    def test_convert_expression_list_nested_list(self):
        expr = [
            "{{ _.a }}",
            [
                "<% $.a %>",
            ]
        ]
        result = ExpressionConverter.convert_list(expr)
        self.assertEquals(result, [
            "{{ ctx().a }}",
            [
                "<% ctx().a %>",
            ]
        ])

    def test_convert_expression_list_nested_dict(self):
        expr = [
            {
                "nested_jinja": "{{ _.a }}",
                "nested_yaql": "<% $.a %>",
            }
        ]
        result = ExpressionConverter.convert_list(expr)
        self.assertEquals(result, [
            {
                "nested_jinja": "{{ ctx().a }}",
                "nested_yaql": "<% ctx().a %>",
            }
        ])

    def test_convert_expression_string_other(self):
        expr = "test some raw string"
        result = ExpressionConverter.convert_string(expr)
        self.assertEquals(result, "test some raw string")

    def test_convert_expression_string_jinja(self):
        expr = "{{ _.test }}"
        result = ExpressionConverter.convert_string(expr)
        self.assertEquals(result, "{{ ctx().test }}")

    def test_convert_expression_string_yaql(self):
        expr = "<% $.test %>"
        result = ExpressionConverter.convert_string(expr)
        self.assertEquals(result, "<% ctx().test %>")
