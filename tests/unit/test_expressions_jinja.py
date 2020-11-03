# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from orquestaconvert.expressions import jinja

from tests import base_test_case


class TestExpressionsJinja(base_test_case.BaseTestCase):
    __test__ = True

    def test_unwrap_expression(self):
        expr = "{{ _.test }}"
        result = jinja.JinjaExpressionConverter.unwrap_expression(expr)
        self.assertEqual(result, "_.test")

    def test_unwrap_expression_nested(self):
        expr = "{{ _.test {{ abc }} }}"
        result = jinja.JinjaExpressionConverter.unwrap_expression(expr)
        self.assertEqual(result, "_.test {{ abc }}")

    def test_unwrap_expression_trim_spaces(self):
        expr = "{{           _.test       }}"
        result = jinja.JinjaExpressionConverter.unwrap_expression(expr)
        self.assertEqual(result, "_.test")

    def test_convert_expression_jinja_context_vars(self):
        expr = "{{ _.test }}"
        result = jinja.JinjaExpressionConverter.convert_string(expr)
        self.assertEqual(result, "{{ ctx().test }}")

    def test_convert_expression_jinja_item_vars(self):
        expr = "{{ _.test }}"
        result = jinja.JinjaExpressionConverter.convert_string(expr, item_vars=['test'])
        self.assertEqual(result, "{{ item(test) }}")

    def test_convert_expression_jinja_context_and_item_vars(self):
        expr = "{{ _.test + _.test2 - _.long_var }}"
        result = jinja.JinjaExpressionConverter.convert_string(expr, item_vars=['test'])
        self.assertEqual(result, "{{ item(test) + ctx().test2 - ctx().long_var }}")

    def test_convert_expression_jinja_function_context_vars(self):
        expr = "{{ list(range(0, _.count)) }}"
        result = jinja.JinjaExpressionConverter.convert_string(expr)
        self.assertEqual(result, "{{ list(range(0, ctx().count)) }}")

    def test_convert_expression_jinja_complex_function_context_vars(self):
        expr = "{{ zip([0, 1, 2], [3, 4, 5], _.all_the_things) }}"
        result = jinja.JinjaExpressionConverter.convert_string(expr)
        self.assertEqual(result, "{{ zip([0, 1, 2], [3, 4, 5], ctx().all_the_things) }}")

    def test_convert_expression_jinja_context_vars_multiple(self):
        expr = "{{ _.test + _.other }}"
        result = jinja.JinjaExpressionConverter.convert_string(expr)
        self.assertEqual(result, "{{ ctx().test + ctx().other }}")

    def test_convert_expression_jinja_context_vars_with_underscore(self):
        expr = "{{ _.test_.other }}"
        result = jinja.JinjaExpressionConverter.convert_string(expr)
        self.assertEqual(result, "{{ ctx().test_.other }}")

    def test_convert_expression_jinja_task_result(self):
        expr = "{{ task('abc').result.result }}"
        result = jinja.JinjaExpressionConverter.convert_string(expr)
        self.assertEqual(result, "{{ result().result }}")

    def test_convert_expression_jinja_task_result_double_quotes(self):
        expr = '{{ task("abc").result.double_quote }}'
        result = jinja.JinjaExpressionConverter.convert_string(expr)
        self.assertEqual(result, "{{ result().double_quote }}")

    def test_convert_expression_jinja_st2kv(self):
        expr = '{{ st2kv.system.test.kv }}'
        result = jinja.JinjaExpressionConverter.convert_string(expr)
        self.assertEqual(result, "{{ st2kv('system.test.kv') }}")

    def test_convert_expression_jinja_st2kv_user(self):
        expr = '{{ st2kv.user.test.kv }}'
        result = jinja.JinjaExpressionConverter.convert_string(expr)
        self.assertEqual(result, "{{ st2kv('user.test.kv') }}")

    def test_convert_expression_jinja_st2_execution_id(self):
        expr = '{{ env().st2_execution_id }}'
        result = jinja.JinjaExpressionConverter.convert_string(expr)
        self.assertEqual(result, "{{ ctx().st2.action_execution_id }}")

    def test_convert_expression_jinja_st2_api_url(self):
        expr = '{{ env().st2_action_api_url }}'
        result = jinja.JinjaExpressionConverter.convert_string(expr)
        self.assertEqual(result, "{{ ctx().st2.api_url }}")
