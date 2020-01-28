import re

from tests.base_test_case import BaseTestCase

from orquestaconvert.expressions import ExpressionConverter
from orquestaconvert.expressions.jinja import JinjaExpressionConverter
from orquestaconvert.expressions.yaql import YaqlExpressionConverter


class TestExpressions(BaseTestCase):
    __test__ = True

    def test_convert_expr_bool(self):
        expr_bool = True
        result = ExpressionConverter.convert(expr_bool)
        self.assertEqual(result, True)
        expr_bool = False
        result = ExpressionConverter.convert(expr_bool)
        self.assertEqual(result, False)

    def test_convert_expr_null(self):
        expr_none = None
        result = ExpressionConverter.convert(expr_none)
        self.assertEqual(result, None)

    def test_convert_expr_int(self):
        expr_int = 0
        result = ExpressionConverter.convert(expr_int)
        self.assertEqual(result, 0)
        expr_int = 100
        result = ExpressionConverter.convert(expr_int)
        self.assertEqual(result, 100)
        expr_int = -1
        result = ExpressionConverter.convert(expr_int)
        self.assertEqual(result, -1)

    def test_convert_expr_obj_with_warning(self):
        expr_obj = object()
        expected_warning_regex = re.compile(
            r"Could not recognize expression '<object object at 0x[0-9a-f]+>'; "
            r"results may not be accurate.")
        with self.assertWarnsRegex(SyntaxWarning, expected_warning_regex):
            result = ExpressionConverter.convert(expr_obj)
        self.assertEqual(result, expr_obj)

    def test_convert_expr_dict(self):
        expr_dict = {"test": "{{ _.value }}"}
        result = ExpressionConverter.convert(expr_dict)
        self.assertEqual(result, {"test": "{{ ctx().value }}"})

    def test_convert_expr_list(self):
        expr_list = ["test", "{{ _.value }}"]
        result = ExpressionConverter.convert(expr_list)
        self.assertEqual(result, ["test", "{{ ctx().value }}"])

    def test_convert_expr_string(self):
        expr_dict = "{{ _.value }}"
        result = ExpressionConverter.convert(expr_dict)
        self.assertEqual(result, "{{ ctx().value }}")

    def test_convert_no_expression(self):
        expr = "data"
        result = ExpressionConverter.convert(expr)
        self.assertEqual(result, "data")

    def test_expression_type_jinja(self):
        expr = "{{ _.test }}"
        result = ExpressionConverter.expression_type(expr)
        self.assertEqual(result, 'jinja')

    def test_expression_type_yaql(self):
        expr = "<% $.test %>"
        result = ExpressionConverter.expression_type(expr)
        self.assertEqual(result, 'yaql')

    def test_expression_type_none(self):
        expr = "test"
        result = ExpressionConverter.expression_type(expr)
        self.assertIsNone(result)

    def test_get_converter_jinja(self):
        expr = "{{ _.test }}"
        result = ExpressionConverter.get_converter(expr)
        self.assertIs(result, JinjaExpressionConverter)

    def test_get_converter_yaql(self):
        expr = "<% $.test %>"
        result = ExpressionConverter.get_converter(expr)
        self.assertIs(result, YaqlExpressionConverter)

    def test_get_converter_none(self):
        expr = "test"
        result = ExpressionConverter.get_converter(expr)
        self.assertIsNone(result)

    def test_unwrap_expression_jinja(self):
        expr = "{{ _.test }}"
        result = ExpressionConverter.unwrap_expression(expr)
        self.assertEqual(result, '_.test')

    def test_unwrap_expression_yaql(self):
        expr = "<% $.test %>"
        result = ExpressionConverter.unwrap_expression(expr)
        self.assertEqual(result, '$.test')

    def test_unwrap_expression_none(self):
        expr = "test"
        result = ExpressionConverter.unwrap_expression(expr)
        self.assertEqual(result, 'test')

    def test_convert_dict(self):
        expr = {
            "jinja_str": "{{ _.test_jinja }}",
            "yaql_str": "<% $.test_yaql %>",
        }
        result = ExpressionConverter.convert_dict(expr)
        self.assertEqual(result, {
            "jinja_str": "{{ ctx().test_jinja }}",
            "yaql_str": "<% ctx().test_yaql %>",
        })

    def test_convert_dict_nested_list(self):
        expr = {
            "expr_list":
            [
                "{{ _.a }}",
                "<% $.a %>",
            ]
        }
        result = ExpressionConverter.convert_dict(expr)
        self.assertEqual(result, {
            "expr_list":
            [
                "{{ ctx().a }}",
                "<% ctx().a %>",
            ]
        })

    def test_convert_dict_nested_dict(self):
        expr = {
            "expr_dict":
            {
                "nested_jinja": "{{ _.a }}",
                "nested_yaql": "<% $.a %>",
            }
        }
        result = ExpressionConverter.convert_dict(expr)
        self.assertEqual(result, {
            "expr_dict":
            {
                "nested_jinja": "{{ ctx().a }}",
                "nested_yaql": "<% ctx().a %>",
            }
        })

    def test_convert_list(self):
        expr = [
            "{{ _.test_jinja }}",
            "<% $.test_yaql %>",
        ]
        result = ExpressionConverter.convert_list(expr)
        self.assertEqual(result, [
            "{{ ctx().test_jinja }}",
            "<% ctx().test_yaql %>",
        ])

    def test_convert_list_nested_list(self):
        expr = [
            "{{ _.a }}",
            [
                "<% $.a %>",
            ]
        ]
        result = ExpressionConverter.convert_list(expr)
        self.assertEqual(result, [
            "{{ ctx().a }}",
            [
                "<% ctx().a %>",
            ]
        ])

    def test_convert_list_nested_dict(self):
        expr = [
            {
                "nested_jinja": "{{ _.a }}",
                "nested_yaql": "<% $.a %>",
            }
        ]
        result = ExpressionConverter.convert_list(expr)
        self.assertEqual(result, [
            {
                "nested_jinja": "{{ ctx().a }}",
                "nested_yaql": "<% ctx().a %>",
            }
        ])

    def test_convert_string_other(self):
        expr = "test some raw string"
        result = ExpressionConverter.convert_string(expr)
        self.assertEqual(result, "test some raw string")

    def test_convert_string_jinja(self):
        expr = "{{ _.test }}"
        result = ExpressionConverter.convert_string(expr)
        self.assertEqual(result, "{{ ctx().test }}")

    def test_convert_string_yaql(self):
        expr = "<% $.test %>"
        result = ExpressionConverter.convert_string(expr)
        self.assertEqual(result, "<% ctx().test %>")
