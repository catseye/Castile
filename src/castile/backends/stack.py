# Compile to some hypothetical stack-based machine.
# Not yet in a good way.

OPS = {
    '+': 'add',
    '-': 'sub',
    '*': 'mul',
    '/': 'div',
    '==': 'eq',
    '!=': 'ne',
    '>': 'gt',
    '>=': 'gte',
    '<': 'lt',
    '<=': 'lte',
}


class Compiler(object):
    def __init__(self, out):
        self.out = out

    def compile(self, ast):
        if ast.type == 'Program':
            self.out.write("""\
; AUTOMATICALLY GENERATED -- EDIT AT OWN RISK

""")
            for child in ast.children:
                self.compile(child)
            self.out.write("""\
""")
        elif ast.type == 'Defn':
            self.out.write('%s:\n' % ast.value)
            self.compile(ast.children[0])
        elif ast.type in ('StructDefn', 'Forward'):
            pass
        elif ast.type == 'FunLit':
            self.out.write('jmp next\n')
            self.out.write('funlit:\n')
            self.compile(ast.children[0])
            self.compile(ast.children[1])
            self.out.write('push nil\n')
            self.out.write('rts\n')
        elif ast.type == 'Args':
            for child in ast.children:
                self.compile(child)
        elif ast.type == 'Arg':
            self.out.write('getarg %s\n' % ast.value)
        elif ast.type == 'Block':
            for child in ast.children:
                self.compile(child)
        elif ast.type == 'VarDecl':
            self.out.write('; push variable %s onto stack\n' % ast.value)
            self.compile(ast.children[0])
        elif ast.type == 'While':
            self.out.write('loop_start:\n')
            self.compile(ast.children[0])
            self.out.write('beq loop_end\n')
            self.compile(ast.children[1])
            self.out.write('jmp loop_start\n')
            self.out.write('loop_end:\n')
        elif ast.type == 'Op':
            self.compile(ast.children[0])
            self.compile(ast.children[1])
            self.out.write('%s\n' % OPS.get(ast.value, ast.value))
        elif ast.type == 'VarRef':
            self.out.write('getvar %s\n' % ast.value)
        elif ast.type == 'FunCall':
            for child in ast.children[1:]:
                self.out.write('; push argument\n')
                self.compile(child)
            self.out.write('; push function\n')
            self.compile(ast.children[0])
            self.out.write('call\n')
        elif ast.type == 'If':
            #~ self.out.write('if (')
            #~ self.compile(ast.children[0])
            #~ self.out.write(') then\n')
            #~ if len(ast.children) == 3:  # if-else
                #~ self.compile(ast.children[1])
                #~ self.out.write(' else\n')
                #~ self.compile(ast.children[2])
            #~ else:  # just-if
                #~ self.compile(ast.children[1])
            #~ self.out.write('end\n')
            pass
        elif ast.type == 'Return':
            self.compile(ast.children[0])
            self.out.write('rts\n')
        elif ast.type == 'Break':
            self.out.write('jmp loop_end\n')
        elif ast.type == 'Not':
            self.compile(ast.children[0])
            self.out.write('not\n')
        elif ast.type == 'None':
            self.out.write('push nil\n')
        elif ast.type == 'BoolLit':
            if ast.value:
                self.out.write("push true\n")
            else:
                self.out.write("push false\n")
        elif ast.type == 'IntLit':
            self.out.write('push %s\n' % ast.value)
        elif ast.type == 'StrLit':
            self.out.write('push %r\n' % ast.value)
        elif ast.type == 'Assignment':
            self.compile(ast.children[1])
            self.out.write('; assign to...')
            self.compile(ast.children[0])
        elif ast.type == 'Make':
            #~ self.out.write('{')
            #~ self.commas(ast.children[1:])
            #~ self.out.write(", '_fieldnames', [")
            #~ for fieldinit in ast.children[1:-1]:
                #~ self.out.write("'%s', " % fieldinit.value)
            #~ self.out.write("'%s'" % ast.children[-1].value)
            #~ self.out.write(']}')
            pass
        elif ast.type == 'FieldInit':
            #~ self.out.write("'%s'," % ast.value)
            #~ self.compile(ast.children[0])
            pass
        elif ast.type == 'Index':
            #~ self.compile(ast.children[0])
            #~ self.out.write('["%s"]' % ast.value)
            pass
        elif ast.type == 'TypeCast':
            #~ self.out.write("['%s'," % ast.value)
            #~ self.compile(ast.children[0])
            #~ self.out.write(']')
            pass
        elif ast.type == 'TypeCase':
            #~ self.out.write('if (')
            #~ self.compile(ast.children[0])
            #~ self.out.write("[0] == '%s')" % ast.value)
            #~ self.out.write('then save=')
            #~ self.compile(ast.children[0])
            #~ self.out.write('\n')
            #~ self.compile(ast.children[0])
            #~ self.out.write('=')
            #~ self.compile(ast.children[0])
            #~ self.out.write('[1]\n')
            #~ self.compile(ast.children[2])
            #~ self.compile(ast.children[0])
            #~ self.out.write(' = save end')
            pass
        else:
            raise NotImplementedError(repr(ast))
