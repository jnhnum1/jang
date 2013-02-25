from functions import Function
from objects import Object, RawObject
from lists import List
from bools import Bool
from strings import String
from numbers import Number
from undefineds import Undefined

from expressions_base import *

class PyExpr(Expr):
    def __init__(self, func):
        self.func = func

    def Eval(self, context):
        return self.func(context)

class BinaryPyExpr(Expr):
    def __init__(self, func):
        self.func = func

    def Eval(self, context):
        this = context.GetVar('this')
        other = context.GetVar('other')
        return self.func(this, other)

class BinaryFunction(Function):
    def __init__(self, f):
        Function.__init__(self, None, ['other'], BinaryPyExpr(f))

def get_object_attributes(context):
    this = context.GetVar('this')
    assert isinstance(this, Object)
    return List(this.AllAttrs())

def clone_object(context):
    this = context.GetVar('this')
    assert isinstance(this, Object)
    return Object(bindings=dict(this.bindings), prototype=this.prototype)

def objects_eq(self, other):
    return Bool(self == other)

def objects_ne(self, other):
    return Bool(self != other)

def objects_le(self, other):
    return Bool(self <= other)

def objects_lt(self, other):
    return Bool(self < other)

def objects_gt(self, other):
    return Bool(self > other)

def objects_ge(self, other):
    return Bool(self >= other)

def objects_to_string(context):
    this = context.GetVar('this')
    return String(str(this))

def string_to_upper(context):
    this = context.GetVar('this')
    return String(str(this).upper())

def string_to_lower(context):
    this = context.GetVar('this')
    return String(str(this).lower())

object_proto = RawObject()
function_proto = Object()
list_proto = Object()
num_proto = Object()
undefined_proto = Object()
bool_proto = Object()
string_proto = Object(prototype=list_proto)
tuple_proto = Object()

string_proto.SetAttr('toUpper', Function(None, [], PyExpr(string_to_upper)))
string_proto.SetAttr('toLower', Function(None, [], PyExpr(string_to_lower)))

object_proto.SetAttr('__eq__', BinaryFunction(objects_eq))
object_proto.SetAttr('__ne__', BinaryFunction(objects_ne))
object_proto.SetAttr('__le__', BinaryFunction(objects_le))
object_proto.SetAttr('__lt__', BinaryFunction(objects_lt))
object_proto.SetAttr('__gt__', BinaryFunction(objects_gt))
object_proto.SetAttr('__ge__', BinaryFunction(objects_ge))

def add_objects(this, other):
    return this + other

def sub_objects(this, other):
    return this - other

def mul_objects(this, other):
    return this * other

def div_objects(this, other):
    return this / other

def pow_objects(this, other):
    return this ** other

def mod_objects(this, other):
    return this % other

object_proto.SetAttr('__add__', BinaryFunction(add_objects))
object_proto.SetAttr('__sub__', BinaryFunction(sub_objects))
object_proto.SetAttr('__mul__', BinaryFunction(mul_objects))
object_proto.SetAttr('__div__', BinaryFunction(div_objects))
object_proto.SetAttr('__pow__', BinaryFunction(pow_objects))
object_proto.SetAttr('__mod__', BinaryFunction(mod_objects))

object_proto.SetAttr('toString', Function(None, [],
    PyExpr(objects_to_string)))

object_proto.SetAttr('items', Function(None, [],
    PyExpr(get_object_attributes)))

object_proto.SetAttr('clone', Function(None, [],
    PyExpr(clone_object)))
def list_length(context):
    this = context.GetVar('this')
    assert isinstance(this, List)
    return Number(len(this.elements))

def list_push(context):
    this = context.GetVar('this')
    assert isinstance(this, List)
    append_elem = context.GetVar('elem')
    this.elements.append(append_elem)
    return Undefined()

def list_pop(context):
    this = context.GetVar('this')
    assert isinstance(this, List)
    return this.elements.pop()

list_proto.SetAttr('length', Function(None, [], PyExpr(list_length)))
list_proto.SetAttr('push', Function(None, ['elem'], PyExpr(list_push)))
list_proto.SetAttr('pop', Function(None, [], PyExpr(list_pop)))

def function_map(context):
    this = context.GetVar('this')
    assert isinstance(this, Function)
    object_list = context.GetVar('list')
    mapped = [this.Call([x]) for x in object_list.elements]
    return List(mapped)

def function_filter(context):
    this = context.GetVar('this')
    assert isinstance(this, Function)
    object_list = context.GetVar('list')
    filtered = [x for x in object_list.elements if this.Call([x]).IsTruthy()]
    return List(filtered)

function_proto.SetAttr('map', Function(None, ['list'],
    PyExpr(function_map)))
function_proto.SetAttr('filter', Function(None, ['list'],
    PyExpr(function_filter)))


