import re
from orquestaconvert.expressions.base import BaseExpressionConverter

# {{ xxx }} -> xxx
UNWRAP_REGEX = r"({{)(.*)(}})"
UNWRAP_PATTERN = re.compile(UNWRAP_REGEX)

# _. -> ctx().
CONTEXT_VARS_REGEX = r"\b(_\.([\w]+))"
CONTEXT_VARS_PATTERN = re.compile(CONTEXT_VARS_REGEX)


class JinjaExpressionConverter(BaseExpressionConverter):

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
