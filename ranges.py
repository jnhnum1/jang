from objects import Object

class Subscriptable(Object):
    '''An object which has integer indexable elements.'''
    def __init__(self, prototype):
        Object.__init__(self, prototype=prototype)

    def GetPySubscriptable(self):
        raise NotImplementedError

    def GetAttr(self, index):
        try:
            index_int = int(index)
            return self.GetIndex(index_int)
        except ValueError:
            return Object.GetAttr(self, index)

    def SetAttr(self, index, value):
        try:
            index_int = int(index)
            self.SetIndex(index_int, value)
        except ValueError:
            # String non-integer index
            return Object.SetAttr(self, index, value)
    
    def Slice(self, lindex, rindex):
        if lindex:
            if rindex:
                return self.__class__(self.GetPySubscriptable()[lindex:rindex])
            else:
                return self.__class__(self.GetPySubscriptable()[lindex:])
        else:
            if rindex:
                return self.__class__(self.GetPySubscriptable()[:rindex])
            else:
                return self.__class__(self.GetPySubscriptable()[:])

class RangeReference(object):
    def __init__(self,
      base_expression, 
      startindex_expression,
      endindex_expression):

      self.base_expression = base_expression
      self.startindex_expression = startindex_expression
      self.endindex_expression = endindex_expression
      self.state = 0
      self.startindex = None
      self.endindex = None

    def Reset(self):
      self.state = 0
      self.base_expression.Reset()
      if self.startindex_expression:
        self.startindex_expression.Reset()
      if self.endindex_expression:
        self.endindex_expression.Reset()

    def Eval(self, context, sub_value):
# TODO this can probably be cleaned up
      self.state += 1
      if self.state == 1:
        return ("eval", context, self.base_expression)
      elif self.state == 2:
        self.evaluated_base = sub_value
        if not isinstance(self.evaluated_base, Subscriptable):
          raise TypeError("Attempted slice of non-subscriptable type")
        if self.startindex_expression:
          return ("eval", context, self.startindex_expression)
        elif self.endindex_expression:
          return ("eval", context, self.endindex_expression)
        else:
          return ("result", None, self)
      elif self.state == 3:
        try:
          if self.startindex_expression:
            self.startindex = int(sub_value.num)
            if self.endindex_expression:
              return ("eval", context, self.endindex_expression)
            else:
              return ("result", None, self)
          elif self.endindex_expression:
            self.endindex = int(sub_value.num)
            return ("result", None, self)
        except:
          raise TypeError("Subscripts must be integers")
      elif self.state == 4:
        try:
          if self.endindex_expression:
            self.endindex = int(sub_value.num)
            return ("result", None, self)
        except:
          raise TypeError("Subscripts must be integers")


    def Get(self, context):
        return self.evaluated_base.Slice(self.startindex, self.endindex)

    def Set(self, val, context):
        self.evaluated_base.SetSlice(self.startindex, self.endindex, val)


class WholeRangeReference(object):
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
      self.evaled_base = sub_value
      return ("result", None, self)

  def Get(self, context):
    return self.evaled_base.Slice()

