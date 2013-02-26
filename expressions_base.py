class Expr(object):
  def Eval(self, context, sub_value):
    raise NotImplementedError(self.__class__.__name__ + ' forgot to'
            'implement Eval()')

class Value(Expr):
  '''An expression which evaluates to itself, e.g. a value (if Eval is not
  overridden)'''
  def Eval(self, context, sub_value):
    return ("result", None, self)
 
  def Reset(self):
    '''Correspondingly, there is a Reset() method which need do nothing for a
    value.'''
    pass

  def IsTruthy(self):
    raise NotImplementedError

class BinaryExpr(Expr):
  '''A general expression for binary operations like +, *, etc.

  This class should be extended with a class field 'method_name' containing
  the name of the attribute that should be called.'''

  def __init__(self, e1, e2):
    self.e1 = e1
    self.e2 = e2

  def Reset(self):
    pass

  def Eval(self, context, sub_value):
    # GAH TODO need to fix circular dependencies
    from expressions import AttributeExpr, AttributeReference
    from functions import FunctionCall
    from strings import String
    method = AttributeExpr(AttributeReference(self.e1,
        String(self.__class__.method_name)))
    return ("tailcall", context, FunctionCall(method, [self.e2],
      is_method=True))

