from objects import Object
from context import Context
from expressions import ReturnValue
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
            # Somebody called new f(arguments)
            obj = Object(prototype=self.constructing_prototype, constructor=self)
            call_context.SetVar('this', obj, local=True) 
            try:
                self.statements.Eval(call_context)
            except ReturnValue as v:
                # The function returned early, but ignore the return value since
                # it was called with new
                pass
            return obj  # Regardless of whether there was an early return.
        try:
            return self.statements.Eval(call_context)
        except ReturnValue as v:
            # The function returned early, so return the returned value
            return v.value

class FuncDeclaration(Expr):

    def __init__(self, param_list, statements):
        self.param_list = param_list 
        self.statements = statements

    def Eval(self, context):
        return Function(context, self.param_list, self.statements)

    def __str__(self):
        return "function(%s) %s" % (', '.join(self.param_list), self.statements)

class FunctionCall(Expr):
    def __init__(self, func_expression, arg_expression_list,
            kw_arg_expressions=None, is_method=False, is_new=False):
        self.func_expression = func_expression
        self.arg_expression_list = arg_expression_list
        if not kw_arg_expressions:
            kw_arg_expressions = {}
        self.kw_arg_expressions = kw_arg_expressions
        self.is_method = is_method
        self.is_new = is_new

    def Eval(self, context):
        func = self.func_expression.Eval(context)
        parent = None
        if self.is_method:
            parent = self.func_expression.GetParent()
        args = [y.Eval(context) for y in self.arg_expression_list]
        kw_args = dict([(k, v.Eval(context)) for k, v in
            self.kw_arg_expressions.items()])
        return func.Call(args, kw_args, parent=parent, is_new=self.is_new)

    def __str__(self):
        return str(self.func_expression) + '(' + str(self.arg_expression_list) + ')'
