from expressions_base import Expr
from ranges import Subscriptable

class ListExpr(Expr):
  '''An expression which when evaluated yields a list.'''

  def __init__(self, element_expressions):
    Expr.__init__(self)
    self.element_expressions = element_expressions
    self.state = 0
    self.evaled_exprs = []

  def Reset(self):
    self.state = 0
    self.evaled_exprs = []
    for expr in self.element_expressions:
      expr.Reset()

  def Eval(self, context, sub_value):
    self.state += 1
    if self.state <= len(self.element_expressions):
      if self.state > 1:
        self.evaled_exprs.append(sub_value)
      return ("eval", context, self.element_expressions[self.state - 1])
    elif self.element_expressions:
      self.evaled_exprs.append(sub_value)
      return ("result", None, List(self.evaled_exprs))


class List(Subscriptable):
    '''An actual list object.'''

    def __init__(self, elements, prototype=None):
        import proto_functions
        if not prototype:
            prototype = proto_functions.list_proto
        Subscriptable.__init__(self, prototype=prototype)
        self.elements = elements

    def GetPySubscriptable(self):
        return self.elements

    def AllAttrs(self):
        indices = set(range(len(self.elements)))
        indices.update(self.GetPrototype().AllAttrs())
        return list(indices)

    def SetSlice(self, lindex, rindex, val):
        if not isinstance(val, List):
            raise TypeError("Subslices can only be set to lists")
        if not lindex and not rindex:
            self.elements[:] = val.elements
        elif lindex and rindex:
            self.elements[lindex:rindex] = val.elements
        elif lindex:
            self.elements[lindex:] = val.elements
        else:
            self.elements[:rindex] = val.elements

    def __add__(self, other):
        return self.__class__(self.elements + other.elements)
    
    def __mul__(self, other):
        try:
            num_times = int(other.num)
        except:
            raise TypeError("Can only multiply lists by integers")
        return self.__class__(self.elements * num_times)

    def __str__(self):
        return '[%s]' % (', '.join([str(e) for e in self.elements]),)

    def __cmp__(self, other):
        return cmp(self.elements, other.elements)

    def GetIndex(self, index):
        return self.elements[index]

    def SetIndex(self, index, value):
        self.elements[index] = value
