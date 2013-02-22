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
        self.startindex = None
        self.endindex = None

    def Evaluate(self, context):
        self.evaluated_base = self.base_expression.Eval(context)
        if (not isinstance(self.evaluated_base, Subscriptable)):
            raise TypeError("Attempted slice of non-subscriptable type")
        try:
            if self.startindex_expression:
                self.startindex = int(self.startindex_expression.Eval(context).num)
            if self.endindex_expression:
                self.endindex = int(self.endindex_expression.Eval(context).num)
        except:
            raise TypeError("Subscripts must be integers")

    def Get(self, context):
        self.Evaluate(context)
        return self.evaluated_base.Slice(self.startindex, self.endindex)

    def Set(self, val, context):
        self.Evaluate(context)
        self.evaluated_base.SetSlice(self.startindex, self.endindex, val)


class WholeRangeReference(object):
    def __init__(self, expression):
        self.expression = expression

    def Get(self, context):
        evaluated_base = self.expression.Eval(context)
        return evaluated_base.Slice()

