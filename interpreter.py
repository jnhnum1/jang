from functions import FunctionCall

# This is a way to intepret a Jang syntax tree non-recursively, with tail-call
# optimization when possible.

def evaluate(expr, context):
  exprStack = [(expr, context)]
  stackFrameTops = []
  if isinstance(expr, FunctionCall):
    stackFrameTops.append(0)
  sub_value = None
  while exprStack:
    (expr, context) = exprStack[-1]
    # print "Expr is ", expr
    (action, context, sub_value) = expr.Eval(context, sub_value)
    if isinstance(sub_value, FunctionCall):
      stackFrameTops.append(len(exprStack))
    if action == "result":
      exprStack.pop()
      # check if we are leaving the current stack frame
      if stackFrameTops and len(exprStack) <= stackFrameTops[-1]:
        stackFrameTops.pop()
    elif action == "eval":
      exprStack.append((sub_value, context))
      sub_value = None # new sub-expressions don't need subvalues
    elif action == "tailcall":
       exprStack[-1] = (sub_value, context)
       sub_value = None # tailcall doesn't need to be passed any initial sub_value
    elif action == "return":
      del exprStack[stackFrameTops[-1]:]
      exprStack.append((sub_value, context))
      stackFrameTops.pop() 
  return sub_value
