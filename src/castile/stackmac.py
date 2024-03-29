# Simple stack machine, mainly for testing the simple
# stack-machine-based backend.

import re

from castile.builtins import BUILTINS
from castile.eval import TaggedValue


labels = {}
debug = False


def boo(b):
    if b:
        return -1
    else:
        return 0


def add_string(strings, s):
    """Adds a string to the pool, deduping it.  Returns the index of the
    entry of the string, whether new or existing."""
    for n, t in enumerate(strings):
        if t == s:
            return n
    strings.append(s)
    return len(strings) - 1


def run(program, strings):
    global labels
    ip = 0
    iter = 0
    stack = []
    callstack = []
    baseptr = 0
    returnsize = 0
    while ip < len(program):
        (op, arg) = program[ip]
        if debug:
            print(ip, op, arg, stack, callstack)
        if op == 'push':
            stack.append(arg)
        elif op == 'pop':
            stack = stack[:-arg]
        elif op == 'dup':
            stack.append(stack[-1])
        elif op == 'jmp':
            ip = arg - 1
        elif op == 'call':
            if isinstance(stack[-1], int):
                callstack.append(ip)
                ip = stack.pop() - 1
            else:  # builtin
                # forget being elegant, let's just do this
                (name, builtin, type) = stack.pop()
                if name == 'print':
                    builtin(strings[stack.pop()])
                elif name == 'concat':
                    b = strings[stack.pop()]
                    a = strings[stack.pop()]
                    pos = add_string(strings, builtin(a, b))
                    stack.append(pos)
                elif name == 'len':
                    a = strings[stack.pop()]
                    stack.append(builtin(a))
                elif name == 'substr':
                    k = stack.pop()
                    p = stack.pop()
                    s = strings[stack.pop()]
                    pos = add_string(strings, builtin(s, p, k))
                    stack.append(pos)
                elif name == 'str':
                    n = stack.pop()
                    pos = add_string(strings, builtin(n))
                    stack.append(pos)
                else:
                    raise NotImplementedError(name)
        elif op == 'rts':
            ip = callstack.pop()
        elif op == 'mul':
            b = stack.pop()
            a = stack.pop()
            stack.append(a * b)
        elif op == 'add':
            b = stack.pop()
            a = stack.pop()
            stack.append(a + b)
        elif op == 'sub':
            b = stack.pop()
            a = stack.pop()
            stack.append(a - b)
        elif op == 'gt':
            b = stack.pop()
            a = stack.pop()
            stack.append(boo(a > b))
        elif op == 'lt':
            b = stack.pop()
            a = stack.pop()
            stack.append(boo(a < b))
        elif op == 'eq':
            b = stack.pop()
            a = stack.pop()
            stack.append(boo(a == b))
        elif op == 'ne':
            b = stack.pop()
            a = stack.pop()
            stack.append(boo(a != b))
        elif op == 'bzero':
            a = stack.pop()
            if a == 0:
                ip = arg - 1
        elif op == 'and':
            b = stack.pop()
            a = stack.pop()
            stack.append(a & b)
        elif op == 'or':
            b = stack.pop()
            a = stack.pop()
            stack.append(a | b)
        elif op == 'not':
            a = stack.pop()
            stack.append(boo(a == 0))
        elif op == 'tag':
            a = stack.pop()
            stack.append(TaggedValue(arg, a))
        elif op == 'set_baseptr':
            stack.append(baseptr)
            baseptr = len(stack) - 1
        elif op == 'set_returnsize':
            returnsize = arg
        elif op == 'clear_baseptr':
            rs = []
            x = 0
            while x < returnsize:
                rs.append(stack.pop())
                x += 1
            target = baseptr + arg
            baseptr = stack[baseptr]
            while len(stack) > target:
                stack.pop()
            x = 0
            while x < returnsize:
                stack.append(rs.pop())
                x += 1
        elif op == 'get_global':
            stack.append(stack[arg])
        elif op == 'get_local':
            stack.append(stack[baseptr + arg])
        elif op == 'set_local':
            stack[baseptr + arg] = stack.pop()
        elif op == 'make_struct':
            if arg > 0:
                struct = stack[-arg:]
                stack = stack[:-arg]
                stack.append(struct)
        elif op == 'get_field':
            obj = stack.pop()
            stack.append(obj[arg])
        elif op == 'get_tag':
            v = stack.pop()
            stack.append(v.tag)
        elif op == 'get_value':
            v = stack.pop()
            stack.append(v.value)
        elif op.startswith('builtin_'):
            (builtin, type) = BUILTINS[op[8:]]
            stack.append((op[8:], builtin, type))
        else:
            raise NotImplementedError((op, arg))
        ip += 1
        iter += 1
        if iter > 10000:
            raise ValueError("infinite loop?")

    if len(stack) > labels['global_pos']:
        result = stack.pop()
        if result == 0:
            result = 'False'
        if result == -1:
            result = 'True'
        print(result)


def main(args):
    address = 0
    program = []
    global labels
    global debug

    if args[1] == '-d':
        args[1] = args[2]
        debug = True

    # load program
    with open(args[1], 'r') as f:
        for line in f:
            line = line.strip()
            match = re.match(r'^(.*?)\;.*$', line)
            if match:
                line = match.group(1)
            line = line.strip()
            if not line:
                continue
            match = re.match(r'^(.*?)\:$', line)
            if match:
                label = match.group(1)
                # print label, address
                labels[label] = address
                continue
            match = re.match(r'^(.*?)\=(-?\d+)$', line)
            if match:
                label = match.group(1)
                pos = int(match.group(2))
                # print label, '=', pos
                labels[label] = pos
                continue
            op = None
            arg = None
            match = re.match(r'^(\w+)\s+(.*?)$', line)
            if match:
                op = match.group(1)
                arg = match.group(2)
            else:
                match = re.match(r'^(\w+)$', line)
                if match:
                    op = match.group(1)
                    arg = None
                else:
                    raise SyntaxError(line)
            program.append((op, arg))
            address += 1

    # resolve labels
    p = []
    strings = []
    for (op, arg) in program:
        if arg in labels:
            p.append((op, labels[arg]))
        elif arg is None:
            p.append((op, arg))
        else:
            match = re.match(r"^'(.*?)'$", arg)
            if match:
                arg = add_string(strings, match.group(1))
            else:
                arg = int(arg)
            p.append((op, arg))

    if debug:
        print(strings)
    run(p, strings)
