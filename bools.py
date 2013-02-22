from objects import Object

class Bool(Object):
    '''A simple boolean object'''
    
    def __init__(self, value):
        import proto_functions
        Object.__init__(self, prototype=proto_functions.bool_proto)
        self.value = value

    def IsTruthy(self):
        return self.value

    def __eq__(self, other):
        return isinstance(other, Bool) and other.value == self.value

    def __neq__(self, other):
        return not (isinstance(other, Bool) and other.value == self.value)

    def __str__(self):
        return "true" if self.value else "false"

