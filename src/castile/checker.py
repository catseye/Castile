from castile.builtins import BUILTINS
from castile.context import ScopedContext
from castile.types import *


class CastileTypeError(ValueError):
    pass


class StructDefinition(object):
    def __init__(self, name, field_names, content_types):
        self.name = name
        self.field_names = field_names  # dict of name -> position
        self.content_types = content_types  # list of types in order

    def field_names_in_order(self):
        m = {}
        for k, v in self.field_names.items():
            m[v] = k
        l = []
        for i in range(len(m)):
            l.append(m[i])
        return l


class TypeChecker(object):
    def __init__(self):
        global_context = {}
        for (name, (value, type)) in BUILTINS.items():
            global_context[name] = type
        self.context = ScopedContext(global_context, level='global')
        self.toplevel_context = ScopedContext({}, self.context, level='toplevel')
        self.context = self.toplevel_context

        self.forwards = {}
        self.structs = {}  # struct name -> StructDefinition
        self.return_type = None
        self.within_control = False

        self.verbose = False

    def set(self, name, type):
        self.context[name] = type
        if self.verbose:
            print('%s: %s' % (name, type))
        return type

    def assert_eq(self, t1, t2):
        if t1 == t2:
            return
        raise CastileTypeError("type mismatch: %s != %s" % (t1, t2))

    def collect_structs(self, ast):
        for child in ast.children:
            if child.tag == 'StructDefn':
                self.collect_struct(child)

    def collect_struct(self, ast):
        name = ast.value
        if name in self.structs:
            raise CastileTypeError('duplicate struct %s' % name)
        struct_fields = {}
        te = []
        i = 0
        for child in ast.children:
            assert child.tag == 'FieldDefn'
            field_name = child.value
            if field_name in struct_fields:
                raise CastileTypeError('already-defined field %s' % field_name)
            struct_fields[field_name] = i
            i += 1
            te.append(self.type_of(child.children[0]))
        self.structs[name] = StructDefinition(ast.value, struct_fields, te)

    def resolve_structs(self, ast):
        if isinstance(ast.type, Struct):
            if ast.type.name not in self.structs:
                raise CastileTypeError('undefined struct %s' % name)
            ast.type.defn = self.structs[ast.type.name]
        for child in ast.children:
            self.resolve_structs(child)

    # context is modified as side-effect of traversal
    def type_of(self, ast):
        if ast.tag == 'Op':
            if ast.value in ('and', 'or'):
                self.assert_eq(self.type_of(ast.children[0]), Boolean())
                self.assert_eq(self.type_of(ast.children[1]), Boolean())
                ast.type = Boolean()
            elif ast.value in ('+', '-', '*', '/'):
                type1 = self.type_of(ast.children[0])
                type2 = self.type_of(ast.children[1])
                self.assert_eq(type1, type2)
                self.assert_eq(type1, Integer())
                ast.type = Integer()
            elif ast.value in ('==', '!=', '>', '>=', '<', '<='):
                type1 = self.type_of(ast.children[0])
                type2 = self.type_of(ast.children[1])
                self.assert_eq(type1, type2)
                ast.type = Boolean()
        elif ast.tag == 'Not':
            type1 = self.type_of(ast.children[0])
            self.assert_eq(type1, Boolean())
            ast.type = Boolean()
        elif ast.tag == 'IntLit':
            ast.type = Integer()
        elif ast.tag == 'StrLit':
            ast.type = String()
        elif ast.tag == 'BoolLit':
            ast.type = Boolean()
        elif ast.tag == 'FunLit':
            save_context = self.context
            self.context = ScopedContext({}, self.toplevel_context,
                                         level='argument')
            self.return_type = None
            arg_types = self.type_of(ast.children[0])  # args
            t = self.type_of(ast.children[1])  # body
            self.assert_eq(t, Void())
            self.context = save_context
            return_type = self.return_type
            self.return_type = None
            if return_type is None:
                return_type = Void()
            ast.type = Function(arg_types, return_type)
        elif ast.tag == 'Args':
            types = []
            for child in ast.children:
                types.append(self.type_of(child))
            return types  # NOT A TYPE
        elif ast.tag == 'Arg':
            ast.type = self.set(ast.value, self.type_of(ast.children[0]))
        elif ast.tag == 'Type':
            map = {
                'integer': Integer(),
                'boolean': Boolean(),
                'string': String(),
                'void': Void(),
            }
            ast.type = map[ast.value]
        elif ast.tag == 'Body':
            self.context = ScopedContext({}, self.context,
                                         level='local')
            self.assert_eq(self.type_of(ast.children[1]), Void())
            self.context = self.context.parent
            ast.type = Void()
        elif ast.tag == 'FunType':
            return_type = self.type_of(ast.children[0])
            ast.type = Function(
                [self.type_of(c) for c in ast.children[1:]], return_type
            )
        elif ast.tag == 'UnionType':
            ast.type = Union([self.type_of(c) for c in ast.children])
        elif ast.tag == 'StructType':
            ast.type = Struct(ast.value)
        elif ast.tag == 'VarRef':
            ast.type = self.context[ast.value]
            ast.aux = self.context.level(ast.value)
        elif ast.tag == 'None':
            ast.type = Void()
        elif ast.tag == 'FunCall':
            t1 = self.type_of(ast.children[0])
            assert isinstance(t1, Function), \
                '%r is not a function' % t1
            if len(t1.arg_types) != len(ast.children) - 1:
                raise CastileTypeError("argument mismatch")
            i = 0
            for child in ast.children[1:]:
                self.assert_eq(self.type_of(child), t1.arg_types[i])
                i += 1
            ast.type = t1.return_type
        elif ast.tag == 'Return':
            t1 = self.type_of(ast.children[0])
            if self.return_type is None:
                self.return_type = t1
            else:
                self.assert_eq(t1, self.return_type)
            ast.type = Void()
        elif ast.tag == 'Break':
            ast.type = Void()
        elif ast.tag == 'If':
            within_control = self.within_control
            self.within_control = True
            t1 = self.type_of(ast.children[0])
            assert t1 == Boolean()
            t2 = self.type_of(ast.children[1])
            if len(ast.children) == 3:
                # TODO useless!  is void.
                t3 = self.type_of(ast.children[2])
                self.assert_eq(t2, t3)
                ast.type = t2
            else:
                ast.type = Void()
            self.within_control = within_control
        elif ast.tag == 'While':
            within_control = self.within_control
            self.within_control = True
            t1 = self.type_of(ast.children[0])
            self.assert_eq(t1, Boolean())
            t2 = self.type_of(ast.children[1])
            ast.type = Void()
            self.within_control = within_control
        elif ast.tag == 'Block':
            for child in ast.children:
                self.assert_eq(self.type_of(child), Void())
            ast.type = Void()
        elif ast.tag == 'Assignment':
            t2 = self.type_of(ast.children[1])
            t1 = None
            name = ast.children[0].value
            if ast.aux == 'defining instance':
                if self.within_control:
                    raise CastileTypeError('definition of %s within control block' % name)
                if name in self.context:
                    raise CastileTypeError('definition of %s shadows previous' % name)
                self.set(name, t2)
                t1 = t2
            else:
                if name not in self.context:
                    raise CastileTypeError('variable %s used before definition' % name)
                t1 = self.type_of(ast.children[0])
            self.assert_eq(t1, t2)
            # not quite useless now (typecase still likes this)
            if self.context.level(ast.children[0].value) != 'local':
                raise CastileTypeError('cannot assign to non-local')
            ast.type = Void()
        elif ast.tag == 'Make':
            t = self.type_of(ast.children[0])
            if t.name not in self.structs:
                raise CastileTypeError("undefined struct %s" % t.name)
            struct_defn = self.structs[t.name]
            if len(struct_defn.content_types) != len(ast.children) - 1:
                raise CastileTypeError("argument mismatch")
            i = 0
            for defn in ast.children[1:]:
                name = defn.value
                t1 = self.type_of(defn)
                pos = struct_defn.field_names[name]
                defn.aux = pos
                self.assert_eq(t1, struct_defn.content_types[pos])
                i += 1
            ast.type = t
        elif ast.tag == 'FieldInit':
            ast.type = self.type_of(ast.children[0])
        elif ast.tag == 'Index':
            t = self.type_of(ast.children[0])
            field_name = ast.value
            struct_fields = self.structs[t.name].field_names
            if field_name not in struct_fields:
                raise CastileTypeError("undefined field")
            index = struct_fields[field_name]
            # we make this value available to compiler backends
            ast.aux = index
            # we look up the type from the StructDefinition
            ast.type = self.structs[t.name].content_types[index]
        elif ast.tag == 'TypeCase':
            t1 = self.type_of(ast.children[0])
            t2 = self.type_of(ast.children[1])
            if not isinstance(t1, Union):
                raise CastileTypeError('bad typecase, %s not a union' % t1)
            if not t1.contains(t2):
                raise CastileTypeError('bad typecase, %s not in %s' % (t2, t1))
            # typecheck t3 with variable in children[0] having type t2
            assert ast.children[0].tag == 'VarRef'
            within_control = self.within_control
            self.within_control = True
            self.context = ScopedContext({}, self.context, level='typecase')
            self.context[ast.children[0].value] = t2
            ast.type = self.type_of(ast.children[2])
            self.context = self.context.parent
            self.within_control = within_control
        elif ast.tag == 'Program':
            for defn in ast.children:
                self.assert_eq(self.type_of(defn), Void())
            ast.type = Void()
            self.resolve_structs(ast)
        elif ast.tag == 'Defn':
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
            ast.type = Void()
        elif ast.tag == 'Forward':
            t = self.type_of(ast.children[0])
            self.forwards[ast.value] = t
            self.set(ast.value, t)
            ast.type = Void()
        elif ast.tag == 'StructDefn':
            ast.type = Void()
        elif ast.tag == 'TypeCast':
            val_t = self.type_of(ast.children[0])
            uni_t = self.type_of(ast.children[1])
            if not isinstance(uni_t, Union):
                raise CastileTypeError('bad cast, not a union: %s' % uni_t)
            if not uni_t.contains(val_t):
                raise CastileTypeError(
                    'bad cast, %s does not include %s' % (uni_t, val_t)
                )
            ast.type = uni_t
        else:
            raise NotImplementedError(repr(ast))
        return ast.type
