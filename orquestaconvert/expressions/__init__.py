import ruamel.yaml.comments
import six
import orquesta.expressions.base

from orquestaconvert.expressions.jinja import JinjaExpressionConverter
from orquestaconvert.expressions.yaql import YaqlExpressionConverter
from orquestaconvert.utils import type_utils


class ExpressionConverter(object):

    @classmethod
    def convert(cls, expr):
        if (isinstance(expr, type_utils.dict_types)):
            return cls.convert_dict(expr)
        elif isinstance(expr, list):
            return cls.convert_list(expr)
        elif isinstance(expr, six.string_types):
            return cls.convert_string(expr)

    @classmethod
    def expression_type(cls, expr):
        for name, evaluator in six.iteritems(orquesta.expressions.base.get_evaluators()):
            if evaluator.has_expressions(expr):
                return name
        return None

    @classmethod
    def get_converter(cls, expr):
        expr_type = cls.expression_type(expr)
        if expr_type == 'jinja':
            return JinjaExpressionConverter
        elif expr_type == 'yaql':
            return YaqlExpressionConverter
        return None

    @classmethod
    def unwarp_expression(cls, expr):
        converter = cls.get_converter(expr)
        if converter:
            return converter.unwrap_expression(expr)
        # this isn't a Jinja or YAQL expression, so return the raw string
        return expr

    @classmethod
    def convert_string(cls, expr):
        # - task('xxx').result -> result()
        #    if 'xxx' != current task name, error
        # - _. -> ctx().
        # - $. -> ctx().
        # - st2kv. -> st2kv('xxx')
        # others?
        converter = cls.get_converter(expr)
        if converter:
            return converter.convert_string(expr)
        # this isn't a Jinja or YAQL expression, so return the raw string
        return expr

    @classmethod
    def convert_dict(cls, expr_dict):
        converted = ruamel.yaml.comments.CommentedMap()
        for k, expr in six.iteritems(expr_dict):
            converted[k] = cls.convert(expr)
        return converted

    @classmethod
    def convert_list(cls, expr_list):
        return [cls.convert(expr) for expr in expr_list]
