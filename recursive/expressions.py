from expressions_base import Expr, Value, BinaryExpr
from bools import Bool
from context import Context, RootGameContext
from objects import Object
from numbers import Number
from strings import String
from undefineds import Undefined

class OpEqualsExpr(Expr):
    '''A general expression for things like +=, -=, etc.
    
    This class should be extended with a class field 'op' mapping to a binary
    expression.'''
    def __init__(self, op, reference, value_expression):
        self.op = op
        self.reference = reference
        self.value_expression = value_expression

    def Eval(self, context):
        old_value = VarAccess(self.reference)
        new_value = self.op(old_value, self.value_expression)
        return AssignExpr(self.reference, new_value).Eval(context)

class InExpr(Value):

    def __init__(self, key_expr, obj_expr):
        self.key_expr = key_expr
        self.obj_expr = obj_expr

    def Eval(self, context):
        key = self.key_expr.Eval(context)
        obj = self.obj_expr.Eval(context)
        if (isinstance(obj, Object) and (isinstance(key, String) or
            (isinstance(key, Number) and isinstance(key.num, int)))):
            return Bool(obj.HasAttr(str(key)))
        else:
            raise TypeError('Invalid subscript types')

class AddExpr(BinaryExpr):
    method_name = '__add__'

class PlusEqualsExpr(OpEqualsExpr):
    op = AddExpr

class SubtractExpr(BinaryExpr):
    method_name = '__sub__'

class MinusEqualsExpr(OpEqualsExpr):
    op = SubtractExpr

class TimesExpr(BinaryExpr):
    method_name = '__mul__'

class ModExpr(BinaryExpr):
    method_name = '__mod__'

class TimesEqualsExpr(OpEqualsExpr):
    op = TimesExpr

class DivExpr(BinaryExpr):
    method_name = '__div__'

class DivEqualsExpr(OpEqualsExpr):
    op = DivExpr

class ExptExpr(BinaryExpr):
    method_name = '__pow__'

class NeExpr(BinaryExpr):
    method_name = '__ne__'

class LtExpr(BinaryExpr):
    method_name = '__lt__'

class GtExpr(BinaryExpr):
    method_name = '__gt__'

class LeExpr(BinaryExpr):
    method_name = '__le__'

class GeExpr(BinaryExpr):
    method_name = '__ge__'

class AndExpr(Expr):
    def __init__(self, x_expr, y_expr):
        self.x_expr = x_expr
        self.y_expr = y_expr

    def Eval(self, context):
        evaled_x = self.x_expr.Eval(context)
        # short-circuiting
        if evaled_x.IsTruthy():
            evaled_y = self.y_expr.Eval(context)
            if evaled_y.IsTruthy():
                return Bool(True)
            else:
                return Bool(False)
        else:
            return Bool(False)

class OrExpr(Expr):
    def __init__(self, x_expr, y_expr):
        self.x_expr = x_expr
        self.y_expr = y_expr

    def Eval(self, context):
        evaled_x = self.x_expr.Eval(context)
        # short-circuiting
        if evaled_x.IsTruthy():
            return Bool(True)
        
        evaled_y = self.y_expr.Eval(context)
        if evaled_y.IsTruthy():
            return Bool(True)
        return Bool(False)

class XorExpr(Expr):
    def __init__(self, x_expr, y_expr):
        self.x_expr = x_expr
        self.y_expr = y_expr

    def Eval(self, context):
        evaled_x = self.x_expr.Eval(context)
        evaled_y = self.y_expr.Eval(context)
        return Bool(evaled_x.IsTruthy() ^ evaled_y.IsTruthy())

class EqualsExpr(BinaryExpr):
    method_name = '__eq__'

class ReturnValue(BaseException):
    '''This is raised as an exception to indicate a function "asynchronously"
    returning.'''
    def __init__(self, value):
        self.value = value

class ReturnExpr(Expr):
    def __init__(self, expression):
        self.expression = expression

    def Eval(self, context):
        evaled = self.expression.Eval(context)
        raise ReturnValue(evaled)


class NotExpr(Expr):
    def __init__(self, expression):
        self.expression = expression

    def Eval(self, context):
        if self.expression.Eval(context).IsTruthy():
            return Bool(False)
        else:
            return Bool(True)

class VarReference(object):
    def __init__(self, var_name):
        self.var_name = var_name

    def Get(self, context):
        return context.GetVar(self.var_name)

    def Set(self, val, context):
        context.SetVar(self.var_name, val)

    def __str__(self):
        return self.var_name

class AttributeReference(object):

    def __init__(self, base_expression, index_expression):
        self.base_expression = base_expression
        self.index_expression = index_expression
        self.evaluated = False

    def Evaluate(self, context):
        self.evaluated_base = self.base_expression.Eval(context)
        self.evaluated_index = self.index_expression.Eval(context)
        if (isinstance(self.evaluated_index, Number) and
                isinstance(self.evaluated_index.num, int)):
            # attribute is an integer
            self.attr_name = str(self.evaluated_index.num)
        elif isinstance(self.evaluated_index, String):
            self.attr_name = self.evaluated_index.elements
        else:
            raise TypeError('Invalid index type: must be int or string')

    def Get(self, context):
        self.Evaluate(context)
        return self.evaluated_base.GetAttr(self.attr_name)

    def Set(self, val, context):
        self.Evaluate(context)
        return self.evaluated_base.SetAttr(self.attr_name, val)

    def GetParent(self):
        '''Must be called after Evaluate()''' 
        return self.evaluated_base

    def __str__(self):
        return "%s.%s" % (self.base_expression, self.index_expression)

class AttributeExpr(Expr):
    def __init__(self, attr_ref):
        self.attr_ref = attr_ref

    def Eval(self, context):
        return self.attr_ref.Get(context)

    def GetParent(self):
        '''Must be called after Eval()'''
        return self.attr_ref.GetParent()

    def __str__(self):
        return str(self.attr_ref)

class VarAccess(Expr):
    def __init__(self, ref):
        self.ref = ref

    def Eval(self, context):
        return self.ref.Get(context)

    def __str__(self):
        return str(self.ref)


class AssignExpr(Expr):
    def __init__(self, var_reference, var_value):
        self.ref = var_reference
        self.val = var_value

    def Eval(self, context):
        evaluated_value = self.val.Eval(context)
        self.ref.Set(evaluated_value, context)
        return evaluated_value

class BlockExpr(Expr):
    def __init__(self, statements):
        self.statements = statements
        self.context = None

    def __str__(self):
        return "{\n%s\n}" % ("\n".join([str(s) for s in self.statements]),)

    def Eval(self, context):
        self.context = Context(context)
        last_result = Undefined()
        for statement in self.statements:
            last_result = statement.Eval(self.context)
        return last_result

class VarDeclaration(Expr):
    def __init__(self, name, val_expr=None, const=False, local=True):
        self.name = name
        self.val_expr = val_expr
        self.const = const
        self.local = local

    def Eval(self, context):
        if self.local:
            context.SetVar(self.name, self.val_expr.Eval(context),
                    const=self.const, local=True)
        else:
            context.SetVar(self.name, self.val_expr.Eval(context),
                    const=self.const)

class DelStatement(Expr):
    def __init__(self, reference):
        self.reference = reference

    def Eval(self, context):
        self.reference.Evaluate(context)
        base = self.reference.evaluated_base
        index = str(self.reference.evaluated_index)
        return Bool(base.DelAttr(index))

class PrintStatement(Expr):
    def __init__(self, expression):
        self.expression = expression

    def Eval(self, context):
        evaled_expression = self.expression.Eval(context)
        context.Output(str(self.expression.Eval(context)))
        return Undefined()
