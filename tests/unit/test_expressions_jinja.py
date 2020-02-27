from tests.base_test_case import BaseTestCase

from orquestaconvert.expressions.jinja import JinjaExpressionConverter


class TestExpressionsJinja(BaseTestCase):
    __test__ = True

    def test_unwrap_expression(self):
        expr = "{{ _.test }}"
        result = JinjaExpressionConverter.unwrap_expression(expr)
        self.assertEqual(result, "_.test")

    def test_unwrap_expression_nested(self):
        expr = "{{ _.test {{ abc }} }}"
        result = JinjaExpressionConverter.unwrap_expression(expr)
        self.assertEqual(result, "_.test {{ abc }}")

    def test_unwrap_expression_trim_spaces(self):
        expr = "{{           _.test       }}"
        result = JinjaExpressionConverter.unwrap_expression(expr)
        self.assertEqual(result, "_.test")

    def test_convert_expression_jinja_context_vars(self):
        expr = "{{ _.test }}"
        result = JinjaExpressionConverter.convert_string(expr)
        self.assertEqual(result, "{{ ctx().test }}")

    def test_convert_expression_jinja_item_vars(self):
        expr = "{{ _.test }}"
        result = JinjaExpressionConverter.convert_string(expr, item_vars=['test'])
        self.assertEqual(result, "{{ item(test) }}")

    def test_convert_expression_jinja_context_and_item_vars(self):
        expr = "{{ _.test + _.test2 - _.long_var }}"
        result = JinjaExpressionConverter.convert_string(expr, item_vars=['test'])
        self.assertEqual(result, "{{ item(test) + ctx().test2 - ctx().long_var }}")

    def test_convert_expression_jinja_function_context_vars(self):
        expr = "{{ list(range(0, _.count)) }}"
        result = JinjaExpressionConverter.convert_string(expr)
        self.assertEqual(result, "{{ list(range(0, ctx().count)) }}")

    def test_convert_expression_jinja_complex_function_context_vars(self):
        expr = "{{ zip([0, 1, 2], [3, 4, 5], _.all_the_things) }}"
        result = JinjaExpressionConverter.convert_string(expr)
        self.assertEqual(result, "{{ zip([0, 1, 2], [3, 4, 5], ctx().all_the_things) }}")

    def test_convert_expression_jinja_context_vars_multiple(self):
        expr = "{{ _.test + _.other }}"
        result = JinjaExpressionConverter.convert_string(expr)
        self.assertEqual(result, "{{ ctx().test + ctx().other }}")

    def test_convert_expression_jinja_context_vars_with_underscore(self):
        expr = "{{ _.test_.other }}"
        result = JinjaExpressionConverter.convert_string(expr)
        self.assertEqual(result, "{{ ctx().test_.other }}")

    def test_convert_expression_jinja_task_result(self):
        expr = "{{ task('abc').result.result }}"
        result = JinjaExpressionConverter.convert_string(expr)
        self.assertEqual(result, "{{ result().result }}")

    def test_convert_expression_jinja_task_result_double_quotes(self):
        expr = '{{ task("abc").result.double_quote }}'
        result = JinjaExpressionConverter.convert_string(expr)
        self.assertEqual(result, "{{ result().double_quote }}")

    def test_convert_expression_jinja_st2kv(self):
        expr = '{{ st2kv.system.test.kv }}'
        result = JinjaExpressionConverter.convert_string(expr)
        self.assertEqual(result, "{{ st2kv('system.test.kv') }}")

    def test_convert_expression_jinja_st2kv_user(self):
        expr = '{{ st2kv.user.test.kv }}'
        result = JinjaExpressionConverter.convert_string(expr)
        self.assertEqual(result, "{{ st2kv('user.test.kv') }}")

    def test_convert_expression_jinja_st2_execution_id(self):
        expr = '{{ env().st2_execution_id }}'
        result = JinjaExpressionConverter.convert_string(expr)
        self.assertEqual(result, "{{ ctx().st2.action_execution_id }}")

    def test_convert_expression_jinja_st2_api_url(self):
        expr = '{{ env().st2_action_api_url }}'
        result = JinjaExpressionConverter.convert_string(expr)
        self.assertEqual(result, "{{ ctx().st2.api_url }}")
