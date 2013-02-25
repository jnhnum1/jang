from expressions_base import Expr
from undefineds import Undefined

class IfElseStatement(Expr):
    def __init__(self, conditionals):
      self.conditionals = conditionals
      self.state = 0

    def Reset(self):
# TODO only reset the things which we have evaled
      self.state = 0
      for hypothesis, statement in self.conditionals:
        hypothesis.Reset()
        statement.Reset()

    def Eval(self, context, sub_value):
      if sub_value and sub_value.IsTruthy():
        return ("tailcall", context, self.conditionals[self.state - 1][1])
      elif self.state < len(self.conditionals):
        self.state += 1
        return ("eval", context, self.conditionals[self.state - 1][0])
      return ("result", None, Undefined())

class WhileStatement(Expr):

    def __init__(self, predicate, body):
        self.pred = predicate
        self.body = body

    def Eval(self, context):
        evaled_pred = self.pred.Eval(context)
        while evaled_pred.IsTruthy():
            self.body.Eval(context)
            evaled_pred = self.pred.Eval(context)
        return Undefined()

