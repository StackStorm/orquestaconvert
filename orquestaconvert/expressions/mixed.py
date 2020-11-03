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
import six
import warnings

import ruamel.yaml.comments

from orquestaconvert import expressions
from orquestaconvert.expressions import base as expr_base
from orquestaconvert.utils import type_utils


# These regexes match Jinja and YAQL expressions, respectively. They are used
# to pick out expressions from strings that contain both types of expressions,
# which we call 'mixed' expressions, in attributes like task actions:
#
# tasks:
#   - do_thing:
#       with-item: target_host in {{ _.target_hosts }}
#       action: ping <% $.ping_flags %> {{ _.target_host }}
#
# Each expression needs to be converted to use the ctx() and item() accessors
# in Orquesta:
#
# tasks:
#   - do_thing:
#       action: ping <% ctx().ping_flags %> {{ item(target_host) }}
#
JINJA_EXPR_RGX = re.compile(r'(?P<expr>(?:{{)\s*.+?\s*(?:}}))')
YAQL_EXPR_RGX = re.compile(r'(?P<expr>(?:<%)\s*.+?\s*(?:%>))')


class MixedExpressionConverter(expr_base.BaseExpressionConverter):
    '''Converter is used to convert all expressions

    Mixed expressions are strings that possibly contain both Jinja and YAQL
    expressions. This converter is used to convert all expressions, regardless
    of their type.
    '''

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
    def convert_string_containing_expressions(cls, match, **kwargs):
        expr = match.group('expr')
        converter = expressions.ExpressionConverter.get_converter(expr)
        if converter:
            expr = converter.unwrap_expression(expr)
            expr = converter.convert_string(expr, **kwargs)
            expr = converter.wrap_expression(expr)

        return expr

    @classmethod
    def convert_string(cls, expr, **kwargs):
        def _inner_convert_string(match):
            return cls.convert_string_containing_expressions(match, **kwargs)
        expr = JINJA_EXPR_RGX.sub(_inner_convert_string, expr)
        expr = YAQL_EXPR_RGX.sub(_inner_convert_string, expr)
        return expr

    @classmethod
    def convert_dict(cls, expr_dict, **kwargs):
        converted = ruamel.yaml.comments.CommentedMap()
        for k, expr in six.iteritems(expr_dict):
            converted[k] = cls.convert(expr, **kwargs)
        return converted

    @classmethod
    def convert_list(cls, expr_list, **kwargs):
        return [cls.convert(expr, **kwargs) for expr in expr_list]
