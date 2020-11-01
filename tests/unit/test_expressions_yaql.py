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

from orquestaconvert.expressions import yaql as yql

from tests import base_test_case


class TestExpressionsYaql(base_test_case.BaseTestCase):
    __test__ = True

    def test_unwrap_expression(self):
        expr = "<% $.test %>"
        result = yql.YaqlExpressionConverter.unwrap_expression(expr)
        self.assertEqual(result, "$.test")

    def test_unwrap_expression_nested(self):
        expr = "<% $.test <% abc %> %>"
        result = yql.YaqlExpressionConverter.unwrap_expression(expr)
        self.assertEqual(result, "$.test <% abc %>")

    def test_unwrap_expression_trim_spaces(self):
        expr = "<%           $.test       %>"
        result = yql.YaqlExpressionConverter.unwrap_expression(expr)
        self.assertEqual(result, "$.test")

    def test_convert_expression_yaql_context_vars(self):
        expr = "<% $.test %>"
        result = yql.YaqlExpressionConverter.convert_string(expr)
        self.assertEqual(result, "<% ctx().test %>")

    def test_convert_expression_yaql_item_vars(self):
        expr = "<% $.test %>"
        result = yql.YaqlExpressionConverter.convert_string(expr, item_vars=['test'])
        self.assertEqual(result, "<% item(test) %>")

    def test_convert_expression_yaql_context_and_item_vars(self):
        expr = "<% $.test + $.test2 - $.long_var %>"
        result = yql.YaqlExpressionConverter.convert_string(expr, item_vars=['test'])
        self.assertEqual(result, "<% item(test) + ctx().test2 - ctx().long_var %>")

    def test_convert_expression_yaql_function_context_vars(self):
        expr = "<% list(range(0, $.count)) %>"
        result = yql.YaqlExpressionConverter.convert_string(expr)
        self.assertEqual(result, "<% list(range(0, ctx().count)) %>")

    def test_convert_expression_yaql_complex_function_context_vars(self):
        expr = "<% zip([0, 1, 2], [3, 4, 5], $.all_the_things) %>"
        result = yql.YaqlExpressionConverter.convert_string(expr)
        self.assertEqual(result, "<% zip([0, 1, 2], [3, 4, 5], ctx().all_the_things) %>")

    def test_convert_expression_yaql_context_vars_multiple(self):
        expr = "<% $.test + $.other %>"
        result = yql.YaqlExpressionConverter.convert_string(expr)
        self.assertEqual(result, "<% ctx().test + ctx().other %>")

    def test_convert_expression_yaql_context_vars_with_underscore(self):
        expr = "<% $.test_.other %>"
        result = yql.YaqlExpressionConverter.convert_string(expr)
        self.assertEqual(result, "<% ctx().test_.other %>")

    def test_convert_expression_yaql_task_result(self):
        expr = "<% task(abc).result.result %>"
        result = yql.YaqlExpressionConverter.convert_string(expr)
        self.assertEqual(result, "<% result().result %>")

    def test_convert_expression_yaql_task_result_single_quote(self):
        expr = "<% task('abc').result.result %>"
        result = yql.YaqlExpressionConverter.convert_string(expr)
        self.assertEqual(result, "<% result().result %>")

    def test_convert_expression_yaql_task_result_double_quotes(self):
        expr = '<% task("abc").result.double_quote %>'
        result = yql.YaqlExpressionConverter.convert_string(expr)
        self.assertEqual(result, "<% result().double_quote %>")

    def test_convert_expression_yaql_st2kv(self):
        expr = '<% st2kv.system.test.kv %>'
        result = yql.YaqlExpressionConverter.convert_string(expr)
        self.assertEqual(result, "<% st2kv('system.test.kv') %>")

    def test_convert_expression_yaql_st2kv_user(self):
        expr = '<% st2kv.user.test.kv %>'
        result = yql.YaqlExpressionConverter.convert_string(expr)
        self.assertEqual(result, "<% st2kv('user.test.kv') %>")

    def test_convert_expression_yaql_st2_execution_id(self):
        expr = '<% env().st2_execution_id %>'
        result = yql.YaqlExpressionConverter.convert_string(expr)
        self.assertEqual(result, "<% ctx().st2.action_execution_id %>")

    def test_convert_expression_yaql_st2_api_url(self):
        expr = '<% env().st2_action_api_url %>'
        result = yql.YaqlExpressionConverter.convert_string(expr)
        self.assertEqual(result, "<% ctx().st2.api_url %>")
