from objects import Object
from context import Context
from expressions_base import Expr
from undefineds import Undefined

class Function(Object):

  def __init__(self, parent_context, param_list, statements):
    import proto_functions
    Object.__init__(self, prototype=proto_functions.function_proto)
    self.parent_context = parent_context
    self.param_list = param_list
    self.statements = statements
    self.constructing_prototype = Object()

  def __str__(self):
    return "function (%s) %s" % (', '.join(self.param_list),
            self.statements)

  def GetAttr(self, attr_name):
    if attr_name == 'prototype':
      return self.constructing_prototype
    return Object.GetAttr(self, attr_name)

  def SetAttr(self, attr_name, attr_value):
    if attr_name == 'prototype':
      self.constructing_prototype = attr_value
      return
    Object.SetAttr(self, attr_name, attr_value)

  def Call(self, arguments, keyword_arguments=None, parent=None, is_new=False):
    # TODO actually handle these keyword arguments
    call_context = Context(self.parent_context)
    for param, value in zip(self.param_list, arguments):
      call_context.SetVar(param, value, local=True)
    # Set any ungiven parameters to undefined
    for param in self.param_list[len(arguments):]:
      call_context.SetVar(param, Undefined(), local=True)
    if parent:
      call_context.SetVar('this', parent, local=True)
    elif is_new:
      # Somebody called new f(arguments).  How can we ignore return values?
      # Never mind that, that is a Javascript wart anyways.  Constructor
      # functions now must explicitly return this.
      obj = Object(prototype=self.constructing_prototype, constructor=self)
      call_context.SetVar('this', obj, local=True) 
    return ("tailcall", call_context, self.statements)

class FuncDeclaration(Expr):

  def __init__(self, param_list, statements):
    self.param_list = param_list 
    self.statements = statements

  def Eval(self, context, sub_value):
    return ("result", None, 
        Function(context, self.param_list, self.statements))

  def __str__(self):
    return "function(%s) %s" % (', '.join(self.param_list), self.statements)

# TODO actually process kw_args
class FunctionCall(Expr):
  def __init__(self, func_expression, arg_expression_list,
          kw_arg_expressions=None, is_method=False, is_new=False):
    self.func_expression = func_expression
    self.arg_expression_list = arg_expression_list
    if not kw_arg_expressions:
      kw_arg_expressions = {}
    self.kw_arg_expressions = kw_arg_expressions
    self.kw_arg_keys = kw_arg_expressions.keys()
    self.is_method = is_method
    self.is_new = is_new
    self.Reset(recurse=False)

  def Reset(self, recurse=True):
    if recurse:
      for expr in self.arg_expression_list:
        expr.Reset()
      self.func_expression.Reset()
      for expr in self.kw_arg_expressions.values():
        expr.Reset()
    self.func_is_evaled = False
    self.evaled_args = []
    self.arg_index = 0
    self.evaled_kw_args = {}
    self.kw_arg_index = 0

  def Eval(self, context, sub_value):
    # First evaluate the function expression, then the arguments, then keyword
    # arguments
    arg_exprs = self.arg_expression_list
    if not self.func_is_evaled:
      self.func_is_evaled = True
      return ("eval", context, self.func_expression)
    elif self.arg_index == 0:
      self.arg_index += 1
      self.evaled_func = sub_value
      if arg_exprs:
        return ("eval", context, arg_exprs[0])
    elif arg_exprs and self.arg_index < len(arg_exprs):
      self.arg_index += 1
      self.evaled_args.append(sub_value)
      return ("eval", context, arg_exprs[self.arg_index - 1])
    elif arg_exprs and self.arg_index == len(arg_exprs):
      self.arg_index += 1
      self.evaled_args.append(sub_value)
    parent = None
    if self.is_method:
        parent = self.func_expression.GetParent()
    return self.evaled_func.Call(self.evaled_args, 
        self.evaled_kw_args, parent=parent, is_new=self.is_new)

  def __str__(self):
    return str(self.func_expression) + '(' + str(self.arg_expression_list) + ')'
