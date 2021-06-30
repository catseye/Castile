class Type(object):
    # Note: type equality relies on (str), so we can't directly
    # compare infinite types.  But with structs, we shouldn't have to.
    def __eq__(self, other):
        return str(self) == str(other)

    def __ne__(self, other):
        return str(self) != str(other)


class Void(Type):
    def __str__(self):
        return "void"


class Integer(Type):
    def __str__(self):
        return "integer"


class String(Type):
    def __str__(self):
        return "string"


class Boolean(Type):
    def __str__(self):
        return "boolean"


class Function(Type):
    def __init__(self, arg_types, return_type):
        self.arg_types = arg_types
        self.return_type = return_type

    def __str__(self):
        h = "function("
        h += ', '.join([str(t) for t in self.arg_types])
        h += '): ' + str(self.return_type)
        return h


class Struct(Type):
    def __init__(self, name):
        self.name = name
        self.defn = None

    def __str__(self):
        return "struct %s" % self.name


class Union(Type):
    def __init__(self, content_types):
        self.content_types = content_types

    def contains(self, type_):
        if isinstance(type_, Union):
            return all([self.contains(t) for t in type_.content_types])
        for member in self.content_types:
            if type_ == member:
                return True
        return False

    def __str__(self):
        h = "union("
        h += ', '.join(sorted([str(t) for t in self.content_types]))
        h += ')'
        return h
