from castile.builtins import BUILTINS
from castile.context import ScopedContext
from castile.types import *


class TypeChecker(object):
    def __init__(self):
        global_context = {}
        for (name, (value, type)) in BUILTINS.iteritems():
            global_context[name] = type
        self.context = ScopedContext(global_context)
        self.context = ScopedContext({}, self.context)

        self.forwards = {}
        self.structs = {}  # struct name -> StructDefinition
        self.struct_fields = {}  # struct name -> dict of field name -> pos
        self.assignable = {}
        self.return_type = None
        self.verbose = False

    def set(self, name, type):
        self.context[name] = type
        if self.verbose:
            print '%s: %s' % (name, type)
        return type

    def assert_eq(self, t1, t2):
        if t1 == t2:
            return
        raise SyntaxError("type mismatch: %s != %s" % (t1, t2))

    def is_assignable(self, ast):
        assert ast.type == 'VarRef'
        name = ast.value
        return name in self.assignable

    def collect_structs(self, ast):
        for child in ast.children:
            if child.type == 'StructDefn':
                self.collect_struct(child)

    def collect_struct(self, ast):
        name = ast.value
        if name in self.structs:
            raise SyntaxError('duplicate struct %s' % name)
        struct_fields = {}
        self.struct_fields[name] = struct_fields
        te = []
        i = 0
        for child in ast.children:
            assert child.type == 'FieldDefn'
            field_name = child.value
            if field_name in struct_fields:
                raise SyntaxError('already-defined field %s' % field_name)
            struct_fields[field_name] = i
            i += 1
            te.append(self.type_of(child.children[0]))
        self.structs[name] = StructDefinition(ast.value, te)

    # context is modified as side-effect of traversal
    def type_of(self, ast):
        if ast.type == 'Op':
            if ast.value in ('and', 'or'):
                self.assert_eq(self.type_of(ast.children[0]), Boolean())
                self.assert_eq(self.type_of(ast.children[1]), Boolean())
                return Boolean()
            elif ast.value in ('+', '-', '*', '/'):
                type1 = self.type_of(ast.children[0])
                type2 = self.type_of(ast.children[1])
                self.assert_eq(type1, type2)
                self.assert_eq(type1, Integer())
                return Integer()
            elif ast.value in ('==', '!=', '>', '>=', '<', '<='):
                type1 = self.type_of(ast.children[0])
                type2 = self.type_of(ast.children[1])
                self.assert_eq(type1, type2)
                return Boolean()
        elif ast.type == 'Not':
            type1 = self.type_of(ast.children[0])
            self.assert_eq(type1, Boolean())
            return Boolean()
        elif ast.type == 'IntLit':
            return Integer()
        elif ast.type == 'StrLit':
            return String()
        elif ast.type == 'FunLit':
            # TODO: should not be able to see anything but globals in here...
            # unless it's a closure.  Oh, joy.
            self.context = ScopedContext({}, self.context)
            self.return_type = None
            arg_types = self.type_of(ast.children[0])  # args
            t = self.type_of(ast.children[1])  # body
            self.assert_eq(t, Void())
            self.context = self.context.parent
            return_type = self.return_type
            self.return_type = None
            if return_type is None:
                return_type = Void()
            # modify AST for compiler's benefit
            ast.children[1].value = 'function body'
            return Function(arg_types, return_type)
        elif ast.type == 'Args':
            types = []
            for child in ast.children:
                types.append(self.type_of(child))
            return types
        elif ast.type == 'Arg':
            return self.set(ast.value, self.type_of(ast.children[0]))
        elif ast.type == 'Type':
            map = {
                'integer': Integer(),
                'boolean': Boolean(),
                'string': String(),
                'void': Void(),
            }
            return map[ast.value]
        elif ast.type == 'FunType':
            return_type = self.type_of(ast.children[0])
            return Function([self.type_of(c) for c in ast.children[1:]],
                            return_type)
        elif ast.type == 'UnionType':
            return Union([self.type_of(c) for c in ast.children])
        elif ast.type == 'StructType':
            return Struct(ast.value)
        elif ast.type == 'VarDecl':
            name = ast.value
            if name in self.context:
                raise SyntaxError('declaration of %s shadows previous' % name)
            self.assignable[name] = True
            self.set(name, self.type_of(ast.children[0]))
            return Void()
        elif ast.type == 'VarRef':
            return self.context[ast.value]
        elif ast.type == 'None':
            return Void()
        elif ast.type == 'FunCall':
            t1 = self.type_of(ast.children[0])
            assert isinstance(t1, Function), \
              '%r is not a function' % t1
            if len(t1.arg_types) != len(ast.children) - 1:
                raise SyntaxError("argument mismatch")
            i = 0
            for child in ast.children[1:]:
                self.assert_eq(self.type_of(child), t1.arg_types[i])
                i += 1
            return t1.return_type
        elif ast.type == 'Return':
            t1 = self.type_of(ast.children[0])
            if self.return_type is None:
                self.return_type = t1
            else:
                self.assert_eq(t1, self.return_type)
            return Void()
        elif ast.type == 'If':
            t1 = self.type_of(ast.children[0])
            assert t1 == Boolean()
            t2 = self.type_of(ast.children[1])
            if len(ast.children) == 3:
                t3 = self.type_of(ast.children[2])
                self.assert_eq(t2, t3)
                return t2
            else:
                return Void()
        elif ast.type == 'While':
            t1 = self.type_of(ast.children[0])
            assert t1 == Boolean()
            t2 = self.type_of(ast.children[1])
            return Void()
        elif ast.type == 'Block':
            self.context = ScopedContext({}, self.context)
            for child in ast.children:
                self.assert_eq(self.type_of(child), Void())
            self.context = self.context.parent
            return Void()
        elif ast.type == 'Assignment':
            t1 = self.type_of(ast.children[0])
            if not self.is_assignable(ast.children[0]):
                raise SyntaxError('cannot assign to non-local')
            t2 = self.type_of(ast.children[1])
            self.assert_eq(t1, t2)
            return Void()
        elif ast.type == 'Make':
            t = self.type_of(ast.children[0])
            if t.name not in self.structs:
                raise SyntaxError("undefined struct %s" % t.name)
            struct_defn = self.structs[t.name]
            if len(struct_defn.content_types) != len(ast.children) - 1:
                raise SyntaxError("argument mismatch")
            i = 0
            for defn in ast.children[1:]:
                t1 = self.type_of(defn)
                self.assert_eq(t1, struct_defn.content_types[i])
                i += 1
            return t
        elif ast.type == 'Index':
            t = self.type_of(ast.children[0])
            field_name = ast.value
            struct_fields = self.struct_fields[t.name]
            if field_name not in struct_fields:
                raise SyntaxError("undefined field")
            index = struct_fields[field_name]
            # we modify the AST for the evaluator's benefit.
            ast.value = index
            # we look up the type from the StructDefinition
            return self.structs[t.name].content_types[index]
        elif ast.type == 'TypeCase':
            t1 = self.type_of(ast.children[0])
            t2 = self.type_of(ast.children[1])

            if not isinstance(t1, Union):
                raise SyntaxError('bad typecase, %s not a union' % t1)
            if not t1.contains(t2):
                raise SyntaxError('bad typecase, %s not in %s' % (t2, t1))
            # modify the AST for the evaluator's benefit
            ast.value = str(t2)

            # typecheck t3 with variable in children[0] having type t2
            assert ast.children[0].type == 'VarRef'
            self.context = ScopedContext({}, self.context)
            self.context[ast.children[0].value] = t2
            t3 = self.type_of(ast.children[2])
            self.context = self.context.parent
            return t3
        elif ast.type == 'Program':
            for defn in ast.children:
                t1 = self.type_of(defn)
            return Void()
        elif ast.type == 'Defn':
            # reset assignable
            self.assignable = {}
            t = self.type_of(ast.children[0])
            if ast.value in self.forwards:
                self.assert_eq(self.forwards[ast.value], t)
                del self.forwards[ast.value]
            else:
                self.set(ast.value, t)
            if ast.value == 'main':
                # any return type is fine, for now, so,
                # we compare it against itself
                rt = t.return_type
                self.assert_eq(t, Function([], rt))
            return t
        elif ast.type == 'Forward':
            t = self.type_of(ast.children[0])
            self.forwards[ast.value] = t
            return self.set(ast.value, t)
        elif ast.type == 'StructDefn':
            pass
        elif ast.type == 'Cast':
            t1 = self.type_of(ast.children[0])
            t2 = self.type_of(ast.children[1])
            if not isinstance(t2, Union):
                raise SyntaxError('bad cast, not a union: %s' % t2)
            if not t2.contains(t1):
                raise SyntaxError('bad cast, %s does not include %s' %
                                  (t2, t1))
            # we modify the ast here for the evaluator's benefit.
            ast.value = str(t1)
            return t2
        else:
            raise NotImplementedError(repr(ast))
