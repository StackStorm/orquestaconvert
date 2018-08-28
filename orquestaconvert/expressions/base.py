import abc
import six


@six.add_metaclass(abc.ABCMeta)
class BaseExpressionConverter(object):

    @classmethod
    @abc.abstractmethod
    def wrap_expression(cls, expr):
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def convert_string(self, expr):
        raise NotImplementedError()
