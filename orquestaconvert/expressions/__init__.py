import ruamel.yaml.comments
import six
from orquestaconvert.expressions import jinja_expr


def convert_expression(expr):
    if (isinstance(expr, dict) or isinstance(expr, ruamel.yaml.comments.CommentedMap)):
        return convert_expression_dict(expr)
    elif isinstance(expr, list):
        return convert_expression_list(expr)
    elif isinstance(expr, six.string_types):
        return convert_expression_string(expr)


def convert_expression_string(expr):
    # TODO convert the Jinja / YAQL expression

    # - task('xxx').result -> result()
    #    if 'xxx' != current task name, error
    # - _. -> ctx().
    # - $. -> ctx().
    # - st2kv. -> st2kv('xxx')
    # others
    return jinja_expr.convert_expression_string(expr)


def convert_expression_dict(expr_dict):
    converted = ruamel.yaml.comments.CommentedMap()
    for k, expr in six.iteritems(expr_dict):
        converted[k] = convert_expression(expr)
    return converted


def convert_expression_list(expr_list):
    return [convert_expression(expr) for expr in expr_list]
