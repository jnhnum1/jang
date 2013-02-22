from expressions_base import Expr
from undefineds import Undefined

class IfElseStatement(Expr):
    def __init__(self, conditionals):
        self.conditionals = conditionals

    def Eval(self, context):
        evaled = Undefined()
        for hypothesis, statement in self.conditionals:
            if hypothesis.Eval(context).IsTruthy():
                evaled = statement.Eval(context)
                break
        return evaled

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

