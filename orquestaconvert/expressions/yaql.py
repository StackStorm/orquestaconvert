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
TASK_RESULT_REGEX = "(task\([\"\']*\w+[\"\']*\).result)"
TASK_RESULT_PATTERN = re.compile(TASK_RESULT_REGEX)

# - st2kv. -> st2kv('xxx')
ST2KV_REGEX = "(st2kv\.([\w\.]+))"
ST2KV_PATTERN = re.compile(ST2KV_REGEX)


class YaqlExpressionConverter(BaseExpressionConverter):

    @classmethod
    def wrap_expression(cls, expr):
        return "<% " + expr + " %>"

    @classmethod
    def unwrap_expression(cls, expr):
        return UNWRAP_PATTERN.sub(cls._replace_unwrap, expr)

    @classmethod
    def convert_context_vars(cls, expr, **kwargs):
        _replace_vars = cls._get_replace_vars(**kwargs)
        return CONTEXT_VARS_PATTERN.sub(_replace_vars, expr)

    @classmethod
    def convert_task_result(cls, expr):
        # TODO error if task name is not the same task in this context
        return TASK_RESULT_PATTERN.sub(cls._replace_task_result, expr)

    @classmethod
    def convert_st2kv(cls, expr):
        return ST2KV_PATTERN.sub(cls._replace_st2kv, expr)
