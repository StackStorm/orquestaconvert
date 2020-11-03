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

from orquestaconvert.expressions import base as expr_base

from tests import base_test_case


class AbstractBaseExpressionsTestCase(base_test_case.BaseTestCase):
    __test__ = True

    def test_wrap_expression_raises(self):
        with self.assertRaises(NotImplementedError):
            expr_base.AbstractBaseExpressionConverter.wrap_expression('junk')

    def test_unwrap_expression_raises(self):
        with self.assertRaises(NotImplementedError):
            expr_base.AbstractBaseExpressionConverter.unwrap_expression('junk')

    def test_convert_string_raises(self):
        with self.assertRaises(NotImplementedError):
            expr_base.AbstractBaseExpressionConverter.convert_string('junk')

    def test_convert_context_vars_raises(self):
        with self.assertRaises(NotImplementedError):
            expr_base.AbstractBaseExpressionConverter.convert_context_vars('junk')

    def test_convert_task_result_raises(self):
        with self.assertRaises(NotImplementedError):
            expr_base.AbstractBaseExpressionConverter.convert_task_result('junk')

    def test_convert_st2kv(self):
        with self.assertRaises(NotImplementedError):
            expr_base.AbstractBaseExpressionConverter.convert_st2kv('junk')

    def test_convert_st2_execution_id(self):
        with self.assertRaises(NotImplementedError):
            expr_base.AbstractBaseExpressionConverter.convert_st2_execution_id('junk')

    def test_convert_st2_api_url(self):
        with self.assertRaises(NotImplementedError):
            expr_base.AbstractBaseExpressionConverter.convert_st2_api_url('junk')


class BaseExpressionsTestCase(base_test_case.BaseTestCase):
    __test__ = True

    def test_wrap_expression_raises(self):
        with self.assertRaises(NotImplementedError):
            expr_base.BaseExpressionConverter.wrap_expression('junk')

    def test_unwrap_expression_raises(self):
        with self.assertRaises(NotImplementedError):
            expr_base.BaseExpressionConverter.unwrap_expression('junk')

    def test_convert_static_string(self):
        with self.assertRaises(NotImplementedError):
            expr_base.BaseExpressionConverter.convert_string('junk')

    def test_convert_static_context_vars_raises(self):
        with self.assertRaises(NotImplementedError):
            expr_base.BaseExpressionConverter.convert_context_vars('junk')
