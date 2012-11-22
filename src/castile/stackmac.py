# Simple stack machine, mainly for testing the simple
# stack-machine-based backend.

import re
import sys

from castile.builtins import BUILTINS


def run(program):
    ip = 0
    stack = []
    callstack = []
    while ip <= len(program):
        (op, arg) = program[ip]
        print ip, op, arg
        if op == 'push':
            stack.append(arg)
        elif op == 'jmp':
            ip = arg - 1
        elif op == 'call':
            callstack.append(ip)
            ip = stack.pop() - 1
        elif op == 'rts':
            ip = callstack.pop()
        else:
            raise NotImplementedError((op, arg))
        ip += 1


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
            p.append((op, arg))

    run(p)
