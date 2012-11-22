from castile.types import Void, String

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
# old baseptr is saved at baseptr + 0
# a is at baseptr + 1
# b is at baseptr + 2

# callee is responsible for popping its locals and the given arguments
# off the stack, and pushing its return value(S) in the space that the
# first argument(S) were occupying

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
        self.loop_end = None
        self.fun_lit = None
        self.fun_argcount = 0
        # 0 = print, 
        self.global_pos = 1     # globals at the bottom of the stack
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

print_index=0

jmp past_print
print:
sys_print
rts
past_print:
push print

""")
            for child in ast.children:
                self.compile(child)
            self.out.write("""\
; ...
global_pos=%d
; call main
get_global main_index
call
""" % self.global_pos)
        elif ast.type == 'Defn':
            self.out.write('%s_index=%d\n' % (ast.value, self.global_pos))
            self.global_pos += 1
            self.compile(ast.children[0])
        elif ast.type in ('StructDefn', 'Forward'):
            pass
        elif ast.type == 'FunLit':
            past_fun = self.get_label('past_fun')
            self.out.write('jmp %s\n' % past_fun)
            save_fun = self.fun_lit
            save_argcount = self.fun_argcount
            self.fun_lit = self.get_label('fun_lit')
            self.local_pos = 1
            self.out.write('%s:\n' % self.fun_lit)
            # also saves the old baseptr right here
            self.out.write('set_baseptr\n')
            self.compile(ast.children[0])
            self.compile(ast.children[1])
            # TODO copy the result value(S) to the first arg position
            # (for now the opcode handles that)
            # TODO must happen before every return!
            self.out.write('exeunt_%s:\n' % self.fun_lit)
            # base this on return type: void = 0, int = 1, union = 2, etc
            returnsize = 1
            if ast.aux.return_type == Void():
                returnsize = 0
            self.out.write('set_returnsize %d\n' % returnsize)
            self.out.write('clear_baseptr %d\n' % (0 - self.fun_argcount))
            self.out.write('rts\n')
            self.out.write('%s:\n' % past_fun)
            self.out.write('push %s\n' % self.fun_lit)
            self.fun_argcount = save_argcount
            self.fun_lit = save_fun
        elif ast.type == 'Args':
            # first arg passed is DEEPEST, so go backwards.
            self.fun_argcount = len(ast.children)
            pos = 0 - self.fun_argcount
            for child in ast.children:
                assert child.type == 'Arg'
                self.out.write('%s_local_%s=%d\n' %
                    (self.fun_lit, child.value, pos))
                pos += 1
        elif ast.type == 'Block':
            for child in ast.children:
                self.compile(child)
        elif ast.type == 'VarDecl':
            self.compile(ast.children[0])
            self.out.write('%s_local_%s=%s\n' %
                (self.fun_lit, ast.value, self.local_pos))
            self.local_pos += 1
        elif ast.type == 'While':
            start = self.get_label('loop_start')
            end = self.get_label('loop_end')
            save = self.loop_end
            self.loop_end = end
            self.out.write('%s:\n' % start)
            self.compile(ast.children[0])
            self.out.write('bzero %s\n' % end)
            self.compile(ast.children[1])
            self.out.write('jmp %s\n' % start)
            self.out.write('%s:\n' % end)
            self.loop_end = self.loop_end
        elif ast.type == 'Op':
            self.compile(ast.children[0])
            self.compile(ast.children[1])
            self.out.write('%s\n' % OPS.get(ast.value, ast.value))
        elif ast.type == 'VarRef':
            if ast.aux in ('toplevel', 'global'):
                self.out.write('get_global %s_index\n' % (ast.value))
            else:
                self.out.write('get_local %s_local_%s\n' % (self.fun_lit, ast.value))
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
            self.out.write('jmp exeunt_%s:\n' % self.fun_lit)
        elif ast.type == 'Break':
            self.out.write('jmp %s\n' % self.loop_end)
        elif ast.type == 'Not':
            self.compile(ast.children[0])
            self.out.write('not\n')
        elif ast.type == 'None':
            pass  # sizeof(void) == 0
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
            self.out.write('set_local %s_local_%s\n' % (self.fun_lit, ast.children[0].value))
        elif ast.type == 'Make':
            for child in ast.children[1:]:
                self.compile(child)
            self.out.write('push %d\n' % (len(ast.children) - 1))
            self.out.write('make_struct\n')  # sigh
        elif ast.type == 'FieldInit':
            self.compile(ast.children[0])
        elif ast.type == 'Index':
            self.compile(ast.children[0])
            self.out.write('get_field %d\n' % ast.aux)
        elif ast.type == 'TypeCast':
            self.compile(ast.children[0])
            self.out.write('; tag with "%s"\n' % ast.value)
            self.out.write('tag 42\n')
        elif ast.type == 'TypeCase':
            end_typecase = self.get_label('end_typecase')
            self.compile(ast.children[0])
            self.out.write('get_tag\n')
            self.out.write('push 42\n')
            self.out.write('eq\n')
            self.out.write('bzero %s\n' % end_typecase)
            # TODO save the value
            # TODO set the value to the untagged value of the value
            self.compile(ast.children[2])
            # TODO restore the value
            self.out.write('%s:\n' % end_typecase)
        else:
            raise NotImplementedError(repr(ast))
