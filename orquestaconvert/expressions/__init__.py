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

import ruamel.yaml.comments
import six
import warnings

import orquesta.expressions.base

from orquestaconvert.expressions import jinja
from orquestaconvert.expressions import yaql as yql
from orquestaconvert.utils import type_utils


class ExpressionConverter(object):

    @classmethod
    def convert(cls, expr, **kwargs):
        if (isinstance(expr, type_utils.dict_types)):
            return cls.convert_dict(expr, **kwargs)
        elif isinstance(expr, list):
            return cls.convert_list(expr, **kwargs)
        elif isinstance(expr, six.string_types):
            return cls.convert_string(expr, **kwargs)
        elif isinstance(expr, bool):
            return expr
        elif expr is None:
            # Note: The only point to explicitly converting None is to skip
            #       emitting the warning. Otherwise we would remove this elif
            #       and let the function return the input. Also, ruamel doesn't
            #       explicitly serialize null to None, it just leaves the key
            #       blank (in other words, it "implicitly" serializes it).
            #       Example:
            #
            #           next:
            #             - when: ...
            #               publish:
            #                 - continue:
            #               ...
            #
            #       See this link for more information:
            #       https://bitbucket.org/ruamel/yaml/issues/169/roundtripdumper-dumps-null-values
            return None
        elif isinstance(expr, int):
            return expr
        else:
            warnings.warn("Could not recognize expression '{}'; results may not "
                          "be accurate.".format(expr), SyntaxWarning)
            return expr

    @classmethod
    def expression_type(cls, expr):
        for name, evaluator in six.iteritems(orquesta.expressions.base.get_evaluators()):
            if evaluator.has_expressions(str(expr)):
                return name
        return None

    @classmethod
    def get_converter(cls, expr):
        expr_type = cls.expression_type(expr)
        if expr_type == 'jinja':
            return jinja.JinjaExpressionConverter
        elif expr_type == 'yaql':
            return yql.YaqlExpressionConverter
        return None

    @classmethod
    def unwrap_expression(cls, expr):
        converter = cls.get_converter(expr)
        if converter:
            return converter.unwrap_expression(expr)
        # this isn't a Jinja or YAQL expression, so return the raw string
        return expr

    @classmethod
    def convert_string(cls, expr, **kwargs):
        # - task('xxx').result -> result()
        #    if 'xxx' != current task name, error
        # - _. -> ctx().
        # - $. -> ctx().
        # - st2kv. -> st2kv('xxx')
        # others?
        converter = cls.get_converter(expr)
        if converter:
            return converter.convert_string(expr, **kwargs)
        # this isn't a Jinja or YAQL expression, so return the raw string
        return expr

    @classmethod
    def convert_dict(cls, expr_dict, **kwargs):
        converted = ruamel.yaml.comments.CommentedMap()
        for k, expr in six.iteritems(expr_dict):
            converted[cls.convert(k, **kwargs)] = cls.convert(expr, **kwargs)
        return converted

    @classmethod
    def convert_list(cls, expr_list, **kwargs):
        return [cls.convert(expr, **kwargs) for expr in expr_list]
