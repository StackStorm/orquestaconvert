import re

# _. -> ctx().
# $. -> ctx().
CONTEXT_VARS_REGEX = "(_\.([\w]+))"
CONTEXT_VARS_PATTERN = re.compile(CONTEXT_VARS_REGEX)

# task('xxx').result -> result()
#    if 'xxx' != current task name, error
TASK_RESULT_REGEX = "(task\([\"\']\w+[\"\']\).result)"
TASK_RESULT_PATTERN = re.compile(TASK_RESULT_REGEX)

# - st2kv. -> st2kv('xxx')
ST2KV_REGEX = "(st2kv\.([\w\.]+))"
ST2KV_PATTERN = re.compile(ST2KV_REGEX)


def convert_expression_string(expr):
    # others?
    expr = convert_context_vars(expr)
    expr = convert_task_result(expr)
    expr = convert_st2kv(expr)
    return expr

def _replace_context_vars(match):
    return "ctx()." + match.group(2)

def convert_context_vars(expr):
    return CONTEXT_VARS_PATTERN.sub(_replace_context_vars, expr)

def _replace_task_result(match):
    return "result()"

def convert_task_result(expr):
    # TODO error if task name is not the same task in this context
    return TASK_RESULT_PATTERN.sub(_replace_task_result, expr)

def _replace_st2kv(match):
    return "st2kv('" + match.group(2) + "')"

def convert_st2kv(expr):
    return ST2KV_PATTERN.sub(_replace_st2kv, expr)
