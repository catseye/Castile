# Compile to some hypothetical stack-based machine.
# Not yet in a good way.

# In a function like this:
#
# fun(x,y,z) {
#   var a = 0;
#   var b = 0;
#   ...
# }
#
# x is at baseptr - 3
# y is at baseptr - 2
# z is at baseptr - 1
# a is at baseptr + 0
# b is at baseptr + 1

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
        self.current_fun_lit = None
        self.global_pos = 0     # globals at the bottom of the stack
        self.local_pos = 0      # locals after the passed arguments

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
get_global main_index
call
""")
        elif ast.type == 'Defn':
            self.out.write('%s_index=%d\n' % (ast.value, self.global_pos))
            self.global_pos += 1
            self.compile(ast.children[0])
        elif ast.type in ('StructDefn', 'Forward'):
            pass
        elif ast.type == 'FunLit':
            l = self.get_label('past_fun')
            self.out.write('jmp %s\n' % l)
            save = self.current_fun_lit
            self.current_fun_lit = self.get_label('fun_lit')
            f = self.current_fun_lit
            self.local_pos = 0  # XXX not quite.  arguments?
            self.out.write('%s:\n' % f)
            self.out.write('set_baseptr\n')
            self.compile(ast.children[0])
            self.compile(ast.children[1])
            self.out.write('%s:\n' % l)
            self.out.write('push %s\n' % f)
            self.current_fun_lit = save
        elif ast.type == 'Args':
            # first arg passed is DEEPEST, so go backwards.
            pos = 0 - len(ast.children)
            for child in ast.children:
                assert child.type == 'Arg'
                self.out.write('%s_local_%s=%d\n' %
                    (self.current_fun_lit, child.value, pos))
                pos += 1
        elif ast.type == 'Block':
            for child in ast.children:
                self.compile(child)
        elif ast.type == 'VarDecl':
            self.compile(ast.children[0])
            self.out.write('%s_local_%s=%s\n' %
                (self.current_fun_lit, ast.value, self.local_pos))
            self.local_pos += 1
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
            if ast.aux == 'toplevel':
                self.out.write('get_global %s_index\n' % (ast.value))
            else:
                self.out.write('get_local %s_local_%s\n' % (self.current_fun_lit, ast.value))
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
            self.out.write('push 0\n')
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
            assert ast.children[0].type == 'VarRef'
            self.out.write('set_local %s_local_%s\n' % (self.current_fun_lit, ast.children[0].value))
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
