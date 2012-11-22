from castile.builtins import BUILTINS


### Evaluator ###


OPS = {
    'and': (lambda x, y: x and y),
    'or': (lambda x, y: x or y),
    '+': (lambda x, y: x + y),
    '-': (lambda x, y: x - y),
    '*': (lambda x, y: x * y),
    '/': (lambda x, y: x / y),
    '==': (lambda x, y: x == y),
    '!=': (lambda x, y: x != y),
    '>=': (lambda x, y: x >= y),
    '<=': (lambda x, y: x <= y),
    '>': (lambda x, y: x > y),
    '<': (lambda x, y: x < y),
}


class TaggedValue(object):
    def __init__(self, tag, value):
        self.tag = tag
        self.value = value

    def __repr__(self):
        return '(%r, %r)' % (self.tag, self.value)


class StructDict(dict):
    def __init__(self, fields):
        dict.__init__(self)
        self.fields = fields

    def __repr__(self):
        h = '{'
        if self.fields:
            for key in self.fields[:-1]:
                h += '%r: %r, ' % (key, self[key])
            h += '%r: %r' % (self.fields[-1], self[self.fields[-1]])
        return h + '}'


class FunctionReturn(Exception):
    pass


# TODO not really a closure
class Closure(object):
    def __init__(self, program, ast):
        self.program = program
        assert callable(ast) or ast.type == 'FunLit'
        self.ast = ast
        self.locals = {}

    def call(self, actuals):
        self.locals = {}
        if callable(self.ast):  # for builtins
            return self.ast(*actuals)
        formals = self.ast.children[0]
        assert formals.type == 'Args'
        i = 0
        for formal in formals.children:
            assert formal.type == 'Arg'
            self.locals[formal.value] = actuals[i]
            i += 1
        try:
            return self.eval()
        except FunctionReturn as e:
            return e.message

    def eval(self, ast=None):
        if ast is None:
            ast = self.ast.children[1]
        if ast.type == 'Block':
            v1 = None
            for stmt in ast.children:
                v1 = self.eval(stmt)
            return v1
        elif ast.type == 'If':
            v1 = self.eval(ast.children[0])
            if len(ast.children) == 3:  # if-else
                if v1:
                    return self.eval(ast.children[1])
                else:
                    return self.eval(ast.children[2])
            else:  # just-if
                if v1:
                    self.eval(ast.children[1])
                return None
        elif ast.type == 'Return':
            v1 = self.eval(ast.children[0])
            raise FunctionReturn(v1)
        elif ast.type == 'While':
            v1 = self.eval(ast.children[0])
            while v1:
                self.eval(ast.children[1])
                v1 = self.eval(ast.children[0])
            return None
        elif ast.type == 'Op':
            v1 = self.eval(ast.children[0])
            op = OPS[ast.value]
            v2 = self.eval(ast.children[1])
            return op(v1, v2)
        elif ast.type == 'Not':
            return not self.eval(ast.children[0])
        elif ast.type == 'VarDecl':
            name = ast.value
            v = self.eval(ast.children[0])
            self.locals[name] = v
            return v
        elif ast.type == 'VarRef':
            name = ast.value
            if name in self.locals:
                return self.locals[name]
            return self.program.stab[name]
        elif ast.type in ['IntLit', 'StrLit']:
            return ast.value
        elif ast.type in ['None']:
            return None
        elif ast.type == 'FunLit':
            return Closure(self.program, ast)
        elif ast.type == 'FunCall':
            fun_val = self.eval(ast.children[0])
            actuals = [self.eval(arg) for arg in ast.children[1:]]
            return fun_val.call(actuals)
        elif ast.type == 'Assignment':
            var_ref = ast.children[0]
            name = var_ref.value
            v = self.eval(ast.children[1])
            self.locals[name] = v
            return None
        elif ast.type == 'Index':
            v = self.eval(ast.children[0])
            return v[ast.value]
        elif ast.type == 'Make':
            v = StructDict([arg.value for arg in ast.children[1:]])
            for arg in ast.children[1:]:
                v[arg.value] = self.eval(arg.children[0])
            return v
        elif ast.type == 'TypeCast':
            return TaggedValue(ast.value, self.eval(ast.children[0]))
        elif ast.type == 'TypeCase':
            r = self.eval(ast.children[0])
            assert isinstance(r, TaggedValue)
            if r.tag == ast.value:
                var_ref = ast.children[0]
                name = var_ref.value
                saved_value = self.locals[name]
                self.locals[name] = r.value
                v = self.eval(ast.children[2])
                self.locals[name] = saved_value
            return None
        else:
            raise NotImplementedError(repr(ast))


class Program(object):
    def __init__(self):
        self.stab = {}
        for (name, (value, type)) in BUILTINS.iteritems():
            if callable(value):
                value = Closure(self, value)
            self.stab[name] = value

    def load(self, ast):
        assert ast.type == 'Program'
        # dummy closure for evaluating literals at toplevel
        toplevel = Closure(self, lambda x: x)
        for child in ast.children:
            if child.type == 'Defn':
                if child.value in self.stab:
                    raise SyntaxError('duplicate definition %s' % child.value)
                self.stab[child.value] = toplevel.eval(child.children[0])

    def run(self):
        return self.stab['main'].call([])
