from base_test_case import BaseActionTestCase

from orquestaconvert.expressions import jinja_expr


class TestExpressionsJinja(BaseActionTestCase):
    __test__ = True

    def test_convert_expression_jinja_context_vars(self):
        expr = "{{ _.test }}"
        result = jinja_expr.convert_expression_string(expr)
        self.assertEquals(result, "{{ ctx().test }}")

    def test_convert_expression_jinja_context_vars_multiple(self):
        expr = "{{ _.test + _.other }}"
        result = jinja_expr.convert_expression_string(expr)
        self.assertEquals(result, "{{ ctx().test + ctx().other }}")

    def test_convert_expression_jinja_context_vars_with_underscore(self):
        expr = "{{ _.test_.other }}"
        result = jinja_expr.convert_expression_string(expr)
        self.assertEquals(result, "{{ ctx().test_.other }}")

    def test_convert_expression_jinja_task_result(self):
        expr = "{{ task('abc').result.result }}"
        result = jinja_expr.convert_expression_string(expr)
        self.assertEquals(result, "{{ result().result }}")

    def test_convert_expression_jinja_task_result_double_quotes(self):
        expr = '{{ task("abc").result.double_quote }}'
        result = jinja_expr.convert_expression_string(expr)
        self.assertEquals(result, "{{ result().double_quote }}")

    def test_convert_expression_jinja_st2kv(self):
        expr = '{{ st2kv.system.test.kv }}'
        result = jinja_expr.convert_expression_string(expr)
        self.assertEquals(result, "{{ st2kv('system.test.kv') }}")

    def test_convert_expression_jinja_st2kv_user(self):
        expr = '{{ st2kv.user.test.kv }}'
        result = jinja_expr.convert_expression_string(expr)
        self.assertEquals(result, "{{ st2kv('user.test.kv') }}")
