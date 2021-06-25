import sys

from castile.types import Boolean, Function, String, Integer, Void, Union


class TaggedValue(object):
    def __init__(self, tag, value):
        self.tag = tag
        self.value = value

    def __repr__(self):
        return '(%r, %r)' % (self.tag, self.value)


def builtin_len(s):
    return len(s)


def builtin_substr(s, start, length):
    return s[start:start + length]


def builtin_print(s):
    """print is ultimately implementation-defined.  Its purpose is to provide
    the contents of a string value to the user in a human-readable fashion.
    Its usage may conflict with the usage of standard output.

    """
    print(s)


def builtin_input(s):
    """input is ultimately implementation-defined.  Its purpose is to obtain
    the contents of a string value from the user in a human-enterable fashion.
    Its usage may conflict with the usage of standard input.

    """
    return raw_input(s)


def builtin_read(n):
    """Read up to n bytes from standard input.  If there are fewer than n
    characters in the returned string, an EOF was encountered.

    """
    return sys.stdin.read(n)


def builtin_write(s):
    """Write the bytes of the string to standard output, returning a count
    of how many were written.  If this is less than the number of characters
    in the string, some problem was encountered.

    """
    return sys.stdout.write(s)


def builtin_concat(s1, s2):
    return s1 + s2


def builtin_int(s):
    try:
        x = int(s)
        return TaggedValue('Type(integer:)', x)
    except ValueError:
        return TaggedValue('Type(void:)', None)


def builtin_str(n):
    return str(n)


def builtin_ord(s):
    return ord(s)


def builtin_chr(n):
    return chr(n)


BUILTINS = {
    'len': (builtin_len, Function([String()], Integer())),
    'print': (builtin_print, Function([String()], Void())),
    'input': (builtin_input, Function([String()], String())),
    'read': (builtin_read, Function([Integer()], String())),
    'write': (builtin_write, Function([String()], Integer())),
    'substr': (builtin_substr,
               Function([String(), Integer(), Integer()], String())),
    'concat': (builtin_concat, Function([String(), String()], String())),
    'int': (builtin_int, Function([String()], Union([Integer(), Void()]))),
    'str': (builtin_str, Function([Integer()], String())),
    'ord': (builtin_ord, Function([String()], Integer())),
    'chr': (builtin_chr, Function([Integer()], String())),
}
