from tests.base_test_case import BaseTestCase

from orquestaconvert.expressions.yaql import YaqlExpressionConverter


class TestExpressionsYaql(BaseTestCase):
    __test__ = True

    def test_unwrap_expression(self):
        expr = "<% $.test %>"
        result = YaqlExpressionConverter.unwrap_expression(expr)
        self.assertEqual(result, "$.test")

    def test_unwrap_expression_nested(self):
        expr = "<% $.test <% abc %> %>"
        result = YaqlExpressionConverter.unwrap_expression(expr)
        self.assertEqual(result, "$.test <% abc %>")

    def test_unwrap_expression_trim_spaces(self):
        expr = "<%           $.test       %>"
        result = YaqlExpressionConverter.unwrap_expression(expr)
        self.assertEqual(result, "$.test")

    def test_convert_expression_yaql_context_vars(self):
        expr = "<% $.test %>"
        result = YaqlExpressionConverter.convert_string(expr)
        self.assertEqual(result, "<% ctx().test %>")

    def test_convert_expression_yaql_item_vars(self):
        expr = "<% $.test %>"
        result = YaqlExpressionConverter.convert_string(expr, item_vars=['test'])
        self.assertEqual(result, "<% item(test) %>")

    def test_convert_expression_yaql_context_and_item_vars(self):
        expr = "<% $.test + $.test2 - $.long_var %>"
        result = YaqlExpressionConverter.convert_string(expr, item_vars=['test'])
        self.assertEqual(result, "<% item(test) + ctx().test2 - ctx().long_var %>")

    def test_convert_expression_yaql_function_context_vars(self):
        expr = "<% list(range(0, $.count)) %>"
        result = YaqlExpressionConverter.convert_string(expr)
        self.assertEqual(result, "<% list(range(0, ctx().count)) %>")

    def test_convert_expression_yaql_complex_function_context_vars(self):
        expr = "<% zip([0, 1, 2], [3, 4, 5], $.all_the_things) %>"
        result = YaqlExpressionConverter.convert_string(expr)
        self.assertEqual(result, "<% zip([0, 1, 2], [3, 4, 5], ctx().all_the_things) %>")

    def test_convert_expression_yaql_context_vars_multiple(self):
        expr = "<% $.test + $.other %>"
        result = YaqlExpressionConverter.convert_string(expr)
        self.assertEqual(result, "<% ctx().test + ctx().other %>")

    def test_convert_expression_yaql_context_vars_with_underscore(self):
        expr = "<% $.test_.other %>"
        result = YaqlExpressionConverter.convert_string(expr)
        self.assertEqual(result, "<% ctx().test_.other %>")

    def test_convert_expression_yaql_task_result(self):
        expr = "<% task(abc).result.result %>"
        result = YaqlExpressionConverter.convert_string(expr)
        self.assertEqual(result, "<% result().result %>")

    def test_convert_expression_yaql_task_result_single_quote(self):
        expr = "<% task('abc').result.result %>"
        result = YaqlExpressionConverter.convert_string(expr)
        self.assertEqual(result, "<% result().result %>")

    def test_convert_expression_yaql_task_result_double_quotes(self):
        expr = '<% task("abc").result.double_quote %>'
        result = YaqlExpressionConverter.convert_string(expr)
        self.assertEqual(result, "<% result().double_quote %>")

    def test_convert_expression_yaql_st2kv(self):
        expr = '<% st2kv.system.test.kv %>'
        result = YaqlExpressionConverter.convert_string(expr)
        self.assertEqual(result, "<% st2kv('system.test.kv') %>")

    def test_convert_expression_yaql_st2kv_user(self):
        expr = '<% st2kv.user.test.kv %>'
        result = YaqlExpressionConverter.convert_string(expr)
        self.assertEqual(result, "<% st2kv('user.test.kv') %>")

    def test_convert_expression_yaql_st2_execution_id(self):
        expr = '<% env().st2_execution_id %>'
        result = YaqlExpressionConverter.convert_string(expr)
        self.assertEqual(result, "<% ctx().st2.action_execution_id %>")

    def test_convert_expression_yaql_st2_api_url(self):
        expr = '<% env().st2_action_api_url %>'
        result = YaqlExpressionConverter.convert_string(expr)
        self.assertEqual(result, "<% ctx().st2.api_url %>")
