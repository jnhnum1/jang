from lists import List
from ranges import Subscriptable

class String(List):

    def __init__(self, elements, prototype=None):
        if not prototype:
            import proto_functions
            prototype = proto_functions.string_proto
        List.__init__(self, elements, prototype=prototype)

    def __eq__(self, other):
        return (isinstance(other, String) and self.elements ==
                other.elements)

    def __neq__(self, other):
        return not self.__eq__(other)
    
    def __cmp__(self, other):
        if not isinstance(other, String):
            return 1
        return cmp(self.elements, other.elements)

    def __str__(self):
        return self.elements

    def __add__(self, other):
        if not isinstance(other, String):
            raise TypeError("Can only concatenate strings with strings")
        return String(self.elements + other.elements)

    def SetSlice(self, val, lindex=None, rindex=None):
        raise TypeError("Cannot mutate strings")

    def GetIndex(self, index):
        return String(self.elements[index])

    def SetIndex(self, index, value):
        raise TypeError('Strings are immutable')
