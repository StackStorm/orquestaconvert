import abc
import re
import six

# task('xxx').result -> result()
#    if 'xxx' != current task name, error
TASK_RESULT_REGEX = r"(task\([\"\']?\w+[\"\']?\).result)"
TASK_RESULT_PATTERN = re.compile(TASK_RESULT_REGEX)

# - st2kv. -> st2kv('xxx')
ST2KV_REGEX = r"(st2kv\.([\w\.]+))"
ST2KV_PATTERN = re.compile(ST2KV_REGEX)


@six.add_metaclass(abc.ABCMeta)
class AbstractBaseExpressionConverter(object):

    @classmethod
    @abc.abstractmethod
    def wrap_expression(cls, expr):
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def unwrap_expression(cls, expr):
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def convert_string(self, expr, **kwargs):
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def convert_context_vars(self, expr, **kwargs):
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def convert_task_result(self, expr, **kwargs):
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def convert_st2kv(self, expr, **kwargs):
        raise NotImplementedError()


class BaseExpressionConverter(AbstractBaseExpressionConverter):

    @classmethod
    def _replace_unwrap(cls, match):
        return match.group(2).strip()

    @classmethod
    def convert_string(cls, expr, **kwargs):
        # others?
        expr = cls.convert_context_vars(expr, **kwargs)
        expr = cls.convert_task_result(expr)
        expr = cls.convert_st2kv(expr)
        return expr

    @classmethod
    def _replace_item_vars(cls, match):
        return "item(" + match.group(2) + ")"

    @classmethod
    def _replace_context_vars(cls, match):
        return "ctx()." + match.group(2)

    @classmethod
    def _get_replace_vars(cls, **kwargs):
        item_vars = kwargs.get('item_vars') or []

        def _inner_replace_vars(match):
            if match and match.group(2) in item_vars:
                return cls._replace_item_vars(match)
            else:
                return cls._replace_context_vars(match)

        return _inner_replace_vars

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
