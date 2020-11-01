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

import re

from orquestaconvert.expressions import base as expr_base

# {{ xxx }} -> xxx
UNWRAP_REGEX = r"({{)(.*)(}})"
UNWRAP_PATTERN = re.compile(UNWRAP_REGEX)

# _. -> ctx().
CONTEXT_VARS_REGEX = r"\b(_\.([\w]+))"
CONTEXT_VARS_PATTERN = re.compile(CONTEXT_VARS_REGEX)


class JinjaExpressionConverter(expr_base.BaseExpressionConverter):

    @classmethod
    def wrap_expression(cls, expr):
        return "{{ " + expr + " }}"

    @classmethod
    def unwrap_expression(cls, expr):
        return UNWRAP_PATTERN.sub(cls._replace_unwrap, expr)

    @classmethod
    def convert_context_vars(cls, expr, **kwargs):
        _replace_vars = cls._get_replace_vars(**kwargs)
        return CONTEXT_VARS_PATTERN.sub(_replace_vars, expr)
