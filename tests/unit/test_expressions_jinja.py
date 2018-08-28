from base_test_case import BaseActionTestCase

from orquestaconvert.expressions.jinja import JinjaExpressionConverter


class TestExpressionsJinja(BaseActionTestCase):
    __test__ = True

    def test_unwrap_expression(self):
        expr = "{{ _.test }}"
        result = JinjaExpressionConverter.unwrap_expression(expr)
        self.assertEquals(result, "_.test")

    def test_unwrap_expression_nested(self):
        expr = "{{ _.test {{ abc }} }}"
        result = JinjaExpressionConverter.unwrap_expression(expr)
        self.assertEquals(result, "_.test {{ abc }}")

    def test_unwrap_expression_trim_spaces(self):
        expr = "{{           _.test       }}"
        result = JinjaExpressionConverter.unwrap_expression(expr)
        self.assertEquals(result, "_.test")

    def test_convert_expression_jinja_context_vars(self):
        expr = "{{ _.test }}"
        result = JinjaExpressionConverter.convert_string(expr)
        self.assertEquals(result, "{{ ctx().test }}")

    def test_convert_expression_jinja_context_vars_multiple(self):
        expr = "{{ _.test + _.other }}"
        result = JinjaExpressionConverter.convert_string(expr)
        self.assertEquals(result, "{{ ctx().test + ctx().other }}")

    def test_convert_expression_jinja_context_vars_with_underscore(self):
        expr = "{{ _.test_.other }}"
        result = JinjaExpressionConverter.convert_string(expr)
        self.assertEquals(result, "{{ ctx().test_.other }}")

    def test_convert_expression_jinja_task_result(self):
        expr = "{{ task('abc').result.result }}"
        result = JinjaExpressionConverter.convert_string(expr)
        self.assertEquals(result, "{{ result().result }}")

    def test_convert_expression_jinja_task_result_double_quotes(self):
        expr = '{{ task("abc").result.double_quote }}'
        result = JinjaExpressionConverter.convert_string(expr)
        self.assertEquals(result, "{{ result().double_quote }}")

    def test_convert_expression_jinja_st2kv(self):
        expr = '{{ st2kv.system.test.kv }}'
        result = JinjaExpressionConverter.convert_string(expr)
        self.assertEquals(result, "{{ st2kv('system.test.kv') }}")

    def test_convert_expression_jinja_st2kv_user(self):
        expr = '{{ st2kv.user.test.kv }}'
        result = JinjaExpressionConverter.convert_string(expr)
        self.assertEquals(result, "{{ st2kv('user.test.kv') }}")
