from expressions_base import Value, Expr

class RawObject(Value):

    def __init__(self, bindings=None, prototype=None, constructor=None):
        Value.__init__(self)
        if not bindings:
            bindings = {}
        self.bindings = bindings
        self.prototype = prototype
        self.constructor = constructor
    
    def __str__(self):
        return '{%s}' % (', '.join(['%s: %s' % (k, v) for k, v in
            self.bindings.items()]),)

    def HasAttr(self, attr_name):
        return attr_name in self.bindings

    def GetAttr(self, attr_name):
        if attr_name in self.bindings:
            return self.bindings[attr_name]
        elif self.prototype:
            return self.prototype.GetAttr(attr_name)
        import undefineds
        return undefineds.Undefined()
    
    def DelAttr(self, attr_name):
        if attr_name in self.bindings:
            del self.bindings[attr_name]
            return True
        else:
            return False

    def AllAttrs(self):
        all_attrs = set(self.bindings.keys())
        if self.prototype:
            all_attrs.update(self.prototype.AllAttrs())
        return list(all_attrs)

    def SetAttr(self, attr_name, attr_value):
        self.bindings[attr_name] = attr_value

    def InvokeMethod(self, method_name, arguments):
        method = self.GetAttr(method_name)
        return method.Call(arguments, parent=self)

    def GetPrototype(self):
        return self.prototype

    def IsTruthy(self):
        return True

    def Clone(self):
        return RawObject(bindings=dict(self.bindings), prototype=self.prototype)

    def Type(self):
        return self.constructor

    def IsInstance(self, other):
        if self.constructor == other:
            return True
        if self.prototype:
            return self.prototype.IsInstance(other)
        return False

class Object(RawObject):

    def __init__(self, bindings=None, prototype=None, constructor=None):
        if not prototype:
            import proto_functions
            prototype = proto_functions.object_proto
        if not constructor:
            constructor=prototype
        RawObject.__init__(self, bindings=bindings, prototype=prototype,
                constructor=constructor)

class ObjectExpression(Expr):
    def __init__(self, expressions):
        self.expressions = expressions
        self.expr_keys = expressions.keys()
        self.state = 0
        self.evaled_items = {}

    def Reset(self):
      self.evaled_items = {}
      self.state = 0

    def Eval(self, context, sub_value):
      self.state += 1
      if self.expr_keys and self.state <= len(self.expr_keys):
        key = self.expr_keys[self.state - 1]
        if self.state > 1:
          oldkey = self.expr_keys[self.state - 2]
          self.evaled_items[oldkey] = sub_value
        return ("eval", context, self.expressions[key])
      if self.expr_keys and self.state > len(self.expr_keys):
        oldkey = self.expr_keys[self.state - 2]
        self.evaled_items[oldkey] = sub_value
      return ("result", None, Object(self.evaled_items))
