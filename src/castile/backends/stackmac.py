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
        self.labels = {}
        self.current_loop_end = None

    def get_label(self, pref):
        count = self.labels.get(pref, 0)
        label = '%s_%d' % (pref, count)
        self.labels[pref] = count + 1
        return label

    def compile(self, ast):
        if ast.type == 'Program':
            self.out.write("""\
; AUTOMATICALLY GENERATED -- EDIT AT OWN RISK

""")
            for child in ast.children:
                self.compile(child)
            self.out.write("""\
; call main
; pick main_index
call
""")
        elif ast.type == 'Defn':
            self.out.write('; define %s_index <count>\n' % ast.value)
            self.compile(ast.children[0])
        elif ast.type in ('StructDefn', 'Forward'):
            pass
        elif ast.type == 'FunLit':
            l = self.get_label('past_fun')
            self.out.write('jmp %s\n' % l)
            f = self.get_label('fun_lit')
            self.out.write('%s:\n' % f)
            self.compile(ast.children[0])
            self.compile(ast.children[1])
            self.out.write('%s:\n' % l)
            self.out.write('push %s\n' % f)
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
            start = self.get_label('loop_start')
            end = self.get_label('loop_end')
            save = self.current_loop_end
            self.current_loop_end = end
            self.out.write('%s:\n' % start)
            self.compile(ast.children[0])
            self.out.write('bzero %s\n' % end)
            self.compile(ast.children[1])
            self.out.write('jmp %s\n' % start)
            self.out.write('%s:\n' % end)
            self.current_loop_end = self.current_loop_end
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
            else_part = self.get_label('else_part')
            end_if = self.get_label('end_if')
            self.compile(ast.children[0])
            self.out.write('bzero %s\n' % else_part)
            self.compile(ast.children[1])
            self.out.write('jmp %s\n' % end_if)
            self.out.write('%s:\n' % else_part)
            if len(ast.children) == 3:
                self.compile(ast.children[2])
            self.out.write('%s:\n' % end_if)
        elif ast.type == 'Return':
            self.compile(ast.children[0])
            self.out.write('rts\n')
        elif ast.type == 'Break':
            self.out.write('jmp %s\n' % self.current_loop_end)
        elif ast.type == 'Not':
            self.compile(ast.children[0])
            self.out.write('not\n')
        elif ast.type == 'None':
            self.out.write('push nil\n')
        elif ast.type == 'BoolLit':
            if ast.value:
                self.out.write("push -1\n")
            else:
                self.out.write("push 0\n")
        elif ast.type == 'IntLit':
            self.out.write('push %s\n' % ast.value)
        elif ast.type == 'StrLit':
            self.out.write('push %r\n' % ast.value)
        elif ast.type == 'Assignment':
            self.compile(ast.children[1])
            self.out.write('; assign to...\n')
            self.compile(ast.children[0])
            self.out.write('assign\n')
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
