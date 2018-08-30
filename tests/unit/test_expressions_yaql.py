from tests.base_test_case import BaseTestCase

from orquestaconvert.expressions.yaql import YaqlExpressionConverter


class TestExpressionsYaql(BaseTestCase):
    __test__ = True

    def test_unwrap_expression(self):
        expr = "<% $.test %>"
        result = YaqlExpressionConverter.unwrap_expression(expr)
        self.assertEquals(result, "$.test")

    def test_unwrap_expression_nested(self):
        expr = "<% $.test <% abc %> %>"
        result = YaqlExpressionConverter.unwrap_expression(expr)
        self.assertEquals(result, "$.test <% abc %>")

    def test_unwrap_expression_trim_spaces(self):
        expr = "<%           $.test       %>"
        result = YaqlExpressionConverter.unwrap_expression(expr)
        self.assertEquals(result, "$.test")

    def test_convert_expression_yaql_context_vars(self):
        expr = "<% $.test %>"
        result = YaqlExpressionConverter.convert_string(expr)
        self.assertEquals(result, "<% ctx().test %>")

    def test_convert_expression_yaql_context_vars_multiple(self):
        expr = "<% $.test + $.other %>"
        result = YaqlExpressionConverter.convert_string(expr)
        self.assertEquals(result, "<% ctx().test + ctx().other %>")

    def test_convert_expression_yaql_context_vars_with_underscore(self):
        expr = "<% $.test_.other %>"
        result = YaqlExpressionConverter.convert_string(expr)
        self.assertEquals(result, "<% ctx().test_.other %>")

    def test_convert_expression_yaql_task_result(self):
        expr = "<% task(abc).result.result %>"
        result = YaqlExpressionConverter.convert_string(expr)
        self.assertEquals(result, "<% result().result %>")

    def test_convert_expression_yaql_task_result_single_quote(self):
        expr = "<% task('abc').result.result %>"
        result = YaqlExpressionConverter.convert_string(expr)
        self.assertEquals(result, "<% result().result %>")

    def test_convert_expression_yaql_task_result_double_quotes(self):
        expr = '<% task("abc").result.double_quote %>'
        result = YaqlExpressionConverter.convert_string(expr)
        self.assertEquals(result, "<% result().double_quote %>")

    def test_convert_expression_yaql_st2kv(self):
        expr = '<% st2kv.system.test.kv %>'
        result = YaqlExpressionConverter.convert_string(expr)
        self.assertEquals(result, "<% st2kv('system.test.kv') %>")

    def test_convert_expression_yaql_st2kv_user(self):
        expr = '<% st2kv.user.test.kv %>'
        result = YaqlExpressionConverter.convert_string(expr)
        self.assertEquals(result, "<% st2kv('user.test.kv') %>")
