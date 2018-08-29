import re
from orquestaconvert.expressions.base import BaseExpressionConverter

# <% xxx %> -> xxx
UNWRAP_REGEX = "(<%)(.*)(%>)"
UNWRAP_PATTERN = re.compile(UNWRAP_REGEX)

# $. -> ctx().
CONTEXT_VARS_REGEX = "(\$\.([\w]+))"
CONTEXT_VARS_PATTERN = re.compile(CONTEXT_VARS_REGEX)

# task('xxx').result -> result()
#    if 'xxx' != current task name, error
TASK_RESULT_REGEX = "(task\([\"\']\w+[\"\']\).result)"
TASK_RESULT_PATTERN = re.compile(TASK_RESULT_REGEX)

# - st2kv. -> st2kv('xxx')
ST2KV_REGEX = "(st2kv\.([\w\.]+))"
ST2KV_PATTERN = re.compile(ST2KV_REGEX)


class YaqlExpressionConverter(BaseExpressionConverter):

    @classmethod
    def wrap_expression(cls, expr):
        return "<% " + expr + " %>"

    @classmethod
    def _replace_unwrap(cls, match):
        return match.group(2).strip()

    @classmethod
    def unwrap_expression(cls, expr):
        return UNWRAP_PATTERN.sub(cls._replace_unwrap, expr)

    @classmethod
    def convert_string(cls, expr):
        # others?
        expr = cls.convert_context_vars(expr)
        expr = cls.convert_task_result(expr)
        expr = cls.convert_st2kv(expr)
        return expr

    @classmethod
    def _replace_context_vars(cls, match):
        return "ctx()." + match.group(2)

    @classmethod
    def convert_context_vars(cls, expr):
        return CONTEXT_VARS_PATTERN.sub(cls._replace_context_vars, expr)

    @classmethod
    def _replace_task_result(cls, match):
        return "result()"

    @classmethod
    def convert_task_result(cls, expr):
        # TODO error if task name is not the same task in this context
        return TASK_RESULT_PATTERN.sub(cls._replace_task_result, expr)

    @classmethod
    def _replace_st2kv(cls, match):
        return "st2kv('" + match.group(2) + "')"

    @classmethod
    def convert_st2kv(cls, expr):
        return ST2KV_PATTERN.sub(cls._replace_st2kv, expr)
