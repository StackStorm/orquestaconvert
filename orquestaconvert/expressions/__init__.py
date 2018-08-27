import ruamel.yaml.comments
import six
import orquesta.expressions.base

from orquestaconvert.expressions import jinja_expr
from orquestaconvert.expressions import yaql_expr


def convert_expression(expr):
    if (isinstance(expr, dict) or isinstance(expr, ruamel.yaml.comments.CommentedMap)):
        return convert_expression_dict(expr)
    elif isinstance(expr, list):
        return convert_expression_list(expr)
    elif isinstance(expr, six.string_types):
        return convert_expression_string(expr)


def convert_expression_string(expr):
    # - task('xxx').result -> result()
    #    if 'xxx' != current task name, error
    # - _. -> ctx().
    # - $. -> ctx().
    # - st2kv. -> st2kv('xxx')
    # others?
    for name, evaluator in six.iteritems(orquesta.expressions.base.get_evaluators()):
        if evaluator.has_expressions(expr):
            if name == 'jinja':
                return jinja_expr.convert_expression_string(expr)
            elif name == 'yaql':
                return yaql_expr.convert_expression_string(expr)

    # this isn't a Jinja or YAQL expression, so return the raw string
    return expr


def convert_expression_dict(expr_dict):
    converted = ruamel.yaml.comments.CommentedMap()
    for k, expr in six.iteritems(expr_dict):
        converted[k] = convert_expression(expr)
    return converted


def convert_expression_list(expr_list):
    return [convert_expression(expr) for expr in expr_list]
