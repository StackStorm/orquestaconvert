import six

def convert_expression(expr):
    # TODO convert the Jinja / YAQL expression
    return expr

def convert_expression_dict(expr_dict):
    converted = {}
    for k, expr in six.iteritems(expr_dict):
        converted[k] = convert_expression(expr)
    return converted

def convert_expression_list(expr_list):
    converted = []
    for expr in expr_list:
        if isinstance(expr, dict):
            converted.append(convert_expression_dict(expr))
        else:
            converted.append(expr)
    return converted
