# Simple stack machine, mainly for testing the simple
# stack-machine-based backend.

import re
import sys

from castile.builtins import BUILTINS


def boo(b):
    if b:
        return -1
    else:
        return 0


def run(program):
    ip = 0
    iter = 0
    stack = []
    callstack = []
    baseptr = 0
    while ip < len(program):
        (op, arg) = program[ip]
        #print ip, op, arg, stack, callstack
        if op == 'push':
            stack.append(arg)
        elif op == 'jmp':
            ip = arg - 1
        elif op == 'call':
            callstack.append(ip)
            ip = stack.pop() - 1
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
        elif op == 'set_baseptr':
            baseptr = len(stack)
        elif op == 'clear_baseptr':
            # TODO assumes only one value returned on stack
            a = stack.pop()
            target = baseptr + arg
            while len(stack) > target:
                stack.pop()
            stack.append(a)
        elif op == 'get_global':
            stack.append(stack[arg])
        elif op == 'get_local':
            stack.append(stack[baseptr + arg])
        elif op == 'set_local':
            stack[baseptr + arg] = stack.pop()
        else:
            raise NotImplementedError((op, arg))
        ip += 1
        iter += 1
        if iter > 10000:
            raise ValueError("infinite loop?")

    result = stack.pop()
    if result != 0:
        print repr(result)


def main(args):
    address = 0
    program = []
    labels = {}
    
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
    for (op, arg) in program:
        if arg in labels:
            p.append((op, labels[arg]))
        else:
            if arg is not None:
                arg = int(arg)
            p.append((op, arg))

    run(p)
