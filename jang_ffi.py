from functions import Function
from lists import List
from numbers import Number
from objects import Object
from strings import String
from tuples import Tuple

def jang_to_py_value(val):
    if isinstance(val, Number):
        return val.num
    if isinstance(val, String):
        return val.elements
    if isinstance(val, List):
        return [jang_to_py_value(x) for x in val.elements]
    if isinstance(val, Function):
        def wrapped(*arguments, **kwargs):
            jang_args = [py_to_jang_value(x) for x in arguments]
            jang_kwargs = dict([(k, py_to_jang_value(v)) for k, v in
                kwargs.items()])
            result = val.Call(jang_args, jang_kwargs)
            py_result = jang_to_py_value(result)
            return py_result
        return wrapped
    if isinstance(val, Tuple):
        return tuple(val.contents)


def py_to_jang_value(val):
    import types
    if isinstance(val, int) or isinstance(val, float):
        return Number(val)
    if isinstance(val, str) or isinstance(val, unicode):
        return String(val)
    if isinstance(val, list):
        return List(val)
    if (isinstance(val, types.FunctionType) or isinstance(val,
            types.BuiltinFunctionType)):
        def wrapped(*arguments, **kwargs):
            py_args = [jang_to_py_value(arg) for arg in arguments]
            py_kwargs = dict([(k, jang_to_py_value(v)) for k, v in
                kwargs.items()])
            result = val(*py_args, **py_kwargs)
            jang_result = py_to_jang_value(result)
            return jang_result
        return PyFunction(wrapped)
    if isinstance(val, types.TupleType):
        return Tuple([py_to_jang_value(x) for x in val])


class PyFunction(Function):
    def __init__(self, func):
        """func is a function which takes Jang values as either positional or
        keyword arguments and returns a Jang value"""
        self.func = func

    def Call(self, arguments, keyword_arguments=None, parent=None, is_new=None):
        if not keyword_arguments:
            keyword_arguments = {}
        return self.func(*arguments, **keyword_arguments)

