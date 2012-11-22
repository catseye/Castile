import sys

from castile.types import Boolean, Function, String, Integer, Void


def builtin_len(s):
    return len(s)


def builtin_substr(s, start, length):
    return s[start:start + length]


def builtin_print(s):
    print s


def builtin_read(n):
    return sys.stdin.read(n)


def builtin_write(n):
    return sys.stdout.write(n)


def builtin_concat(s1, s2):
    return s1 + s2


BUILTINS = {
    'len': (builtin_len, Function([String()], Integer())),
    'print': (builtin_print, Function([String()], Void())),
    'read': (builtin_read, Function([Integer()], String())),
    'write': (builtin_write, Function([String()], Integer())),
    'substr': (builtin_substr,
               Function([String(), Integer(), Integer()], String())),
    'concat': (builtin_concat, Function([String(), String()], String())),
}
