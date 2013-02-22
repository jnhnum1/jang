class Expr(object):

    def Eval(self, context):
        raise NotImplementedError(self.__class__.__name__ + ' forgot to'
                'implement Eval()')

class Value(Expr):
    '''An expression which evaluates to itself, e.g. a value'''

    def Eval(self, context):
        return self

    def IsTruthy(self):
        raise NotImplementedError

class BinaryExpr(Expr):
    '''A general expression for binary operations like +, *, etc.

    This class should be extended with a class field 'method_name' containing
    the name of the attribute that should be called.'''

    def __init__(self, e1, e2):
        self.e1 = e1
        self.e2 = e2

    def Eval(self, context):
        evaled_e1 = self.e1.Eval(context)
        evaled_e2 = self.e2.Eval(context)
        method_name = self.__class__.method_name
        return evaled_e1.InvokeMethod(method_name, [evaled_e2])

