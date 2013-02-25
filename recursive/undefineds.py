from objects import Object

class Undefined(Object):
    def __init__(self):
        import proto_functions
        Object.__init__(self, prototype=proto_functions.undefined_proto)

    def IsTruthy(self):
        return False

    def __eq__(self, other):
        return isinstance(other, Undefined)

    def __neq__(self, other):
        return not isinstance(other, Undefined)

    def __str__(self):
        return "undefined"

