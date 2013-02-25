# This is a way to intepret a Jang syntax tree non-recursively, with tail-call
# optimization when possible.

def evaluate(expr, env):
  exprStack = [(expr, env)]
  stackFrameTops = [0]
  sub_value = None
  while exprStack:
    (expr, env) = exprStack[-1]
    (action, env, sub_value) = expr.Eval(env, sub_value)
    if action == "result":
      exprStack.pop()
      # check if we are leaving the current stack frame
      if len(exprStack) <= stackFrameTops[-1]:
        stackFrameTops.pop()
    elif action == "eval":
      exprStack.append((sub_value, env))
      if isinstance(sub_value, FunctionCall):
        stackFrameTops.append(len(exprStack))
      sub_value = None # new sub-expressions don't need subvalues
    elif action == "tailcall":
       exprStack[-1] = (sub_value, env)
       sub_value = None # tailcall doesn't need to be passed any initial sub_value
    elif action == "return":
      del exprStack[stackFrameTops[-1]:]
      exprStack.append((env, sub_value))
      stackFrameTops.pop() 
  return sub_value
