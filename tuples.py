from expressions_base import Expr
from objects import Object
from ranges import Subscriptable

class TupleExpression(Expr):
    def __init__(self, contents):
        self.contents = contents

    def Eval(self, context):
        evaled_contents = [v.Eval(context) for v in self.contents]
        return Tuple(evaled_contents)

class Tuple(Subscriptable):
    def __init__(self, contents):
        import proto_functions
        Object.__init__(self, prototype=proto_functions.tuple_proto)
        self.contents = contents

    def __add__(self, other):
        return Tuple(self.contents + other.contents)

    def SetSlice(self, lindex, rindex, val):
        raise TypeError('Tuples are immutable')

    def GetIndex(self, index):
        return self.contents[index]

    def SetIndex(self, index, value):
        raise TypeError('Tuples are immutable')

    def __str__(self):
        return '(%s)' % (', '.join([str(s) for s in self.contents]),)

