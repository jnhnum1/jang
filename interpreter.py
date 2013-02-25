# This is a way to intepret a Jang syntax tree non-recursively, with tail-call
# optimization when possible.

def evaluate(expr, env):
  exprStack = [(expr, env)]
  stackFrameTops = [0]
  subValue = None
  while exprStack:
    (expr, env) = exprStack[-1]
    (action, env, subValue) = expr.Eval(env, subValue)
    if action == "result":
      exprStack.pop()
      # check if we are leaving the current stack frame
      if len(exprStack) <= stackFrameTops[-1]:
        stackFrameTops.pop()
    elif action == "eval":
      exprStack.append((subValue, env))
      if isinstance(subValue, FunctionCall):
        stackFrameTops.append(len(exprStack))
      subValue = None # new sub-expressions don't need subvalues
    elif action == "tailcall":
       exprStack[-1] = (subValue, env)
       subValue = None # tailcall doesn't need to be passed any initial subValue
    elif action == "return":
      del exprStack[stackFrameTops[-1]:]
      exprStack.append((env, subValue))
      stackFrameTops.pop() 
  return subValue
