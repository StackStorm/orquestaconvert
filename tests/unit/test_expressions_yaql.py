from base_test_case import BaseActionTestCase

from orquestaconvert.expressions import yaql_expr


class TestExpressionsYaql(BaseActionTestCase):
    __test__ = True

    def test_convert_expression_yaql_context_vars(self):
        expr = "<% $.test %>"
        result = yaql_expr.convert_expression_string(expr)
        self.assertEquals(result, "<% ctx().test %>")

    def test_convert_expression_yaql_context_vars_multiple(self):
        expr = "<% $.test + $.other %>"
        result = yaql_expr.convert_expression_string(expr)
        self.assertEquals(result, "<% ctx().test + ctx().other %>")

    def test_convert_expression_yaql_context_vars_with_underscore(self):
        expr = "<% $.test_.other %>"
        result = yaql_expr.convert_expression_string(expr)
        self.assertEquals(result, "<% ctx().test_.other %>")

    def test_convert_expression_yaql_task_result(self):
        expr = "<% task('abc').result.result %>"
        result = yaql_expr.convert_expression_string(expr)
        self.assertEquals(result, "<% result().result %>")

    def test_convert_expression_yaql_task_result_double_quotes(self):
        expr = '<% task("abc").result.double_quote %>'
        result = yaql_expr.convert_expression_string(expr)
        self.assertEquals(result, "<% result().double_quote %>")

    def test_convert_expression_yaql_st2kv(self):
        expr = '<% st2kv.system.test.kv %>'
        result = yaql_expr.convert_expression_string(expr)
        self.assertEquals(result, "<% st2kv('system.test.kv') %>")

    def test_convert_expression_yaql_st2kv_user(self):
        expr = '<% st2kv.user.test.kv %>'
        result = yaql_expr.convert_expression_string(expr)
        self.assertEquals(result, "<% st2kv('user.test.kv') %>")
