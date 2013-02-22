from undefineds import Undefined
from bools import Bool

class Context(object):

    def __init__(self, parent=None):
        self.var_bindings = {}
        self.consts = set()
        self.transients = set()
        self.parent = parent
        self.AddTransients()

    def __getstate__(self):
        # These methods are used for pickling
        bindings = dict(self.var_bindings)
        for transient in self.transients:
            del bindings[transient]
        return {'var_bindings' : bindings,
                'consts' : self.consts,
                'transients' : set(),
                'parent' : self.parent}

    def __setstate__(self, state):
        self.var_bindings = state['var_bindings']
        self.consts = state['consts']
        self.transients = state['transients']
        self.parent = state['parent']
        self.AddTransients()

    def AddTransients(self):
        pass

    def GetVar(self, var_name):
        cur_context= self
        while cur_context is not None:
            if var_name in cur_context.var_bindings:
                return cur_context.var_bindings[var_name]
            cur_context = cur_context.parent
        raise NameError('%s is not defined.' % (var_name,))

    def SetVar(self, var_name, var_value=None, const=False, local=False,
            transient=False):
        if var_name in self.var_bindings:
            # Check that we are not trying to redeclare it.
            if const or local or transient:
                raise NameError('%s is already defined; cannot redeclare it' %
                        (var_name,))
            elif var_name not in self.consts:
                self.var_bindings[var_name] = var_value
            else:
                raise NameError('%s is a constant; cannot change its value.' %
                        (var_name,))
        elif local:
            if not var_value:
                var_value = Undefined()
            # Jang allows shadowing constants, so we don't need to check
            # whether parent contexts contain this var_name
            self.var_bindings[var_name] = var_value
            if const:
                self.consts.add(var_name)
            if transient:
                self.transients.add(var_name)
        elif not self.parent:
            self.var_bindings[var_name] = var_value
            if const:
                self.consts.add(var_name)
            if transient:
                self.transients.add(var_name)
        else:
            self.parent.SetVar(var_name, var_value, const=const,
                    transient=transient)

    def __str__(self):
        return_dict = dict(self.var_bindings.items())
        context = self.parent
        while context:
            return_dict.update(context.var_bindings)
            context = context.parent
        return_dict = dict([(k, str(v)) for k, v in return_dict.items()])
        return str(return_dict)

    def Output(self, value):
        print value

    def Return(self, value):
        pass

def handleGameError(x):
    raise Exception(x)

class RootGameContext(Context):

    def AddTransients(self):
        from jang_ffi import PyFunction
        self.SetVar('tell', PyFunction(lambda x: self.SendMessage(x.elements)),
                const=True, transient=True)
        self.SetVar('type', PyFunction(lambda x: x.Type()), const=True,
                transient=True)
        self.SetVar('isinstance', PyFunction(lambda x, y: Bool(x.IsInstance(y))), const=True,
                transient=True)
        self.SetVar('error', PyFunction(handleGameError), const=True,
            transient=True)
        self.SetVar('endGame', PyFunction(lambda msg: self.EndGame(msg)), const=True,
                transient=True)

    def SendMessage(self, msg):
        print msg
        self.message_queue.append(msg)

    def EndGame(self, msg):
        self.game_over = True

    def __init__(self):
        Context.__init__(self)
        import proto_functions
        self.SetVar('List', proto_functions.list_proto, const=True)
        self.SetVar('Function', proto_functions.function_proto, const=True)
        self.SetVar('Object', proto_functions.object_proto, const=True)
        self.SetVar('Number', proto_functions.num_proto, const=True)
        self.SetVar('Boolean', proto_functions.bool_proto, const=True)
        self.SetVar('String', proto_functions.string_proto, const=True)
        self.message_queue = []
        self.game_over = False
