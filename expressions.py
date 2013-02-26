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

  def Reset(self):
    self.reference.Reset()
    self.value_expression.Reset()

  def Eval(self, context, sub_value):
    old_value = RefAccess(self.reference)
    new_value = self.op(old_value, self.value_expression)
    return ("tailcall", context, AssignExpr(self.reference, new_value))


class InExpr(Value):

  def __init__(self, key_expr, obj_expr):
    self.key_expr = key_expr
    self.obj_expr = obj_expr
    self.state = 0

  def Reset(self):
    self.state = 0
    self.key_expr.Reset()
    self.obj_expr.Reset()

  def Eval(self, context, sub_value):
    self.state += 1
    if self.state == 1:
      return ("eval", context, self.key_expr)
    elif self.state == 2:
      self.evaled_key = sub_value
      return ("eval", context, self.obj_expr)
    else:
      obj = sub_value
      key = self.evaled_key
      if (isinstance(obj, Object) and (isinstance(key, String) or
        (isinstance(key, Number) and isinstance(key.num, int)))):
        return ("result", None, Bool(obj.HasAttr(str(key))))
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
    self.state = 0

  def Reset(self):
    self.state = 0
    self.x_expr.Reset()
    self.y_expr.Reset()

  def Eval(self, context, sub_value):
    self.state += 1
    if self.state == 1:
      return ("eval", context, self.x_expr)
    else:
      # short-circuiting
      self.evaled_x = sub_value
      if self.evaled_x.IsTruthy():
        return ("tailcall", context, self.y_expr)
      else:
        return ("result", None, self.evaled_x)


class OrExpr(Expr):
  def __init__(self, x_expr, y_expr):
    self.x_expr = x_expr
    self.y_expr = y_expr
    self.state = 0

  def Reset(self):
    self.state = 0
    self.x_expr.Reset()
    self.y_expr.Reset()

  def Eval(self, context, sub_value):
    self.state += 1
    if self.state == 1:
      return ("eval", context, self.x_expr)
    else:
      self.evaled_x = sub_value
      if self.evaled_x.IsTruthy():
        return ("result", None, self.evaled_x)
      else:
        return ("tailcall", context, self.y_expr)


class XorExpr(Expr):
  def __init__(self, x_expr, y_expr):
    self.x_expr = x_expr
    self.y_expr = y_expr
    self.state = 0

  def Reset(self):
    self.state = 0
    self.x_expr.Reset()
    self.y_expr.Reset()

  def Eval(self, context, sub_value):
    self.state += 1
    if self.state == 1:
      return ("eval", context, self.x_expr)
    elif self.state == 2:
      self.evaled_x = sub_value
      return ("eval", context, self.y_expr)
    else:
      self.evaled_y = sub_value
      return ("result", None,
                Bool(self.evaled_x.IsTruthy() ^ self.evaled_y.IsTruthy()))


class EqualsExpr(BinaryExpr):
  method_name = '__eq__'


class ReturnExpr(Expr):
  def __init__(self, expression):
    self.expression = expression

  def Reset(self):
    self.expression.Reset()

  def Eval(self, context, sub_value):
    return ("return", context, self.expression)


class NotExpr(Expr):
  def __init__(self, expression):
    self.expression = expression
    self.state = 0

  def Reset(self):
    self.state = 0
    self.expression.Reset()

  def Eval(self, context, sub_value):
    self.state += 1
    if self.state == 1:
      return ("eval", context, self.expression)
    else:
      if sub_value.IsTruthy():
        return ("result", None, Bool(False))
      else:
        return ("result", None, Bool(True))


class VarReference(object):
  def __init__(self, var_name):
    self.var_name = var_name

  def Reset(self):
    pass

  def Get(self, context):
    return context.GetVar(self.var_name)

  def Set(self, val, context):
    context.SetVar(self.var_name, val)

  def Eval(self, context, sub_value):
    # do nothing
    return ("result", None, self)

  def __str__(self):
    return self.var_name

class AttributeReference(object):

  def __init__(self, base_expression, index_expression):
    self.base_expression = base_expression
    self.index_expression = index_expression
    self.state = 0

  def Reset(self):
    self.state = 0
    self.base_expression.Reset()
    self.index_expression.Reset()

  def Eval(self, context, sub_value):
    self.state += 1
    if self.state == 1:
      return ("eval", context, self.base_expression)
    elif self.state == 2:
      self.evaluated_base = sub_value
      return ("eval", context, self.index_expression)
    else:
      self.evaluated_index = sub_value
      if (isinstance(self.evaluated_index, Number) and
            isinstance(self.evaluated_index.num, int)):
        # attribute is an integer
        self.attr_name = str(self.evaluated_index.num)
      elif isinstance(self.evaluated_index, String):
        self.attr_name = self.evaluated_index.elements
      else:
        raise TypeError('Invalid index type: must be int or string')
      return ("result", None, self)

  def Get(self, context):
    return self.evaluated_base.GetAttr(self.attr_name)

  def Set(self, val, context):
    return self.evaluated_base.SetAttr(self.attr_name, val)

  def GetParent(self):
    '''Must be called after Evaluate()''' 
    return self.evaluated_base

  def __str__(self):
    return "%s.%s" % (self.base_expression, self.index_expression)


class AttributeExpr(Expr):
  def __init__(self, attr_ref):
    self.attr_ref = attr_ref
    self.evaled_ref = None
    self.state = 0
  
  def Reset(self):
    self.state = 0
    self.attr_ref.Reset()
    self.evaled_ref = None

  def Eval(self, context, sub_value):
    self.state += 1
    if self.state == 1:
      return ("eval", context, self.attr_ref)
    else:
      self.evaled_ref = sub_value
      return ("result", None, sub_value.Get(context))

  def GetParent(self):
    '''Must be called after Eval()'''
    return self.evaled_ref.GetParent()

  def __str__(self):
    return str(self.attr_ref)


class RefAccess(Expr):
  def __init__(self, ref):
    self.ref = ref
    self.state = 0

  def Reset(self):
    self.state = 0
    self.ref.Reset()

  def Eval(self, context, sub_value):
    return ("result", None, self.ref.Get(context))

  def __str__(self):
    return str(self.ref)


class AssignExpr(Expr):

  def __init__(self, var_reference, var_value):
    self.ref = var_reference
    self.val = var_value
    self.state = 0

  def Reset(self):
    self.state = 0
    self.ref.Reset()
    self.val.Reset()

  def Eval(self, context, sub_value):
    self.state += 1
    if self.state == 1:
      return ("eval", context, self.val)
    elif self.state == 2:
      self.evaled_val = sub_value
      return ("eval", context, self.ref)
    else:
      sub_value.Set(self.evaled_val, context)
      return ("result", None, self.evaled_val) 

class BlockExpr(Expr):
  def __init__(self, statements):
      self.statements = statements
      self.current_index = 0

  def Reset(self):
    self.current_index = 0
    for statement in self.statements:
      statement.Reset()

  def __str__(self):
      return "{\n%s\n}" % ("\n".join([str(s) for s in self.statements]),)

  def Eval(self, context, sub_value):
    if len(self.statements) == 0:
      return ("result", None, Undefined())
    elif self.current_index == len(self.statements) - 1:
      return ("tailcall", context, self.statements[self.current_index])
    else:
      self.current_index += 1
      return ("eval", context, self.statements[self.current_index - 1])

class VarDeclaration(Expr):
  def __init__(self, name, val_expr=None, const=False, local=True):
    self.name = name
    if not val_expr:
      val_expr = Undefined()
    self.val_expr = val_expr
    self.const = const
    self.local = local
    self.state = 0

  def Reset(self):
    self.state = 0
    if self.val_expr:
      self.val_expr.Reset()

  def Eval(self, context, sub_value):
    self.state += 1
    if self.state == 1:
      return ("eval", context, self.val_expr)
    else:
      if self.local:
        context.SetVar(self.name, sub_value,
                const=self.const, local=True)
      else:
        context.SetVar(self.name, sub_value,
                const=self.const)
      return ("result", None, sub_value)

class DelStatement(Expr):
  def __init__(self, reference):
    self.reference = reference
    self.state = 0

  def Reset(self):
    self.state = 0
    self.reference.Reset()

  def Eval(self, context, sub_value):
    self.state += 1
    if self.state == 1:
      return ("eval", context, self.reference)
    else:
      base = sub_value.evaluated_base
      index = str(sub_value.evaluated_index)
      return ("result", None, Bool(base.DelAttr(index)))

class PrintStatement(Expr):
  def __init__(self, expression):
    self.expression = expression
    self.state = 0

  def Reset(self):
    self.state = 0
    self.expression.Reset()

  def Eval(self, context, sub_value):
    self.state += 1
    if self.state == 1:
      return ("eval", context, self.expression)
    context.Output(str(sub_value))
    return ("result", None, Undefined())
