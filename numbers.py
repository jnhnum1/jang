from objects import Object
from lists import List

class Number(Object):
    def __init__(self, num):
        import proto_functions
        Object.__init__(self, prototype=proto_functions.num_proto)
        self.num = num

    def __add__(self, other):
        if not isinstance(other, Number):
            raise TypeError("Can only add numbers to numbers")
        return Number(self.num + other.num)

    def __mul__(self, other):
        if isinstance(other, List): # can multiply
            return other.Times(self)
        return Number(self.num * other.num)

    def __div__(self, other):
        return Number(self.num / other.num)

    def __sub__(self, other):
        return Number(self.num - other.num)

    def __pow__(self, other):
        return Number(self.num ** other.num)

    def __mod__(self, other):
        return Number(self.num % other.num)

    def IsTruthy(self):
        return self.num != 0

    def __cmp__(self, other):
        if not isinstance(other, Number):
            raise TypeError('Cannot compare Number to non-Number')
        return cmp(self.num, other.num)
    
    def __eq__(self, other):
        return isinstance(other, Number) and self.num == other.num

    def __neq__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return str(self.num)

