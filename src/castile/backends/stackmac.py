from castile.types import Void, String

# Compile to some hypothetical stack-based machine.
# Not yet in a good way.

# A big difference between this and the higher-level backends is that
# values of type void have size zero, i.e. nothing is pushed onto the
# stack for them.  (Giving them a nominal value would possibly make
# this easier.)

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
        self.fun_lit = None     # string id'ing current fun being gend
        self.fun_argsize = 0    # number of stack slots taken by args
        self.global_pos = 0     # globals at the bottom of the stack
        self.local_pos = 0      # locals after the passed arguments
        self.tags = {}          # numeric tags established so far
        self.tag_count = 0      # next tag to generate

    def size_of(self, ast):
        if ast.type == 'Type':
            if ast.value == 'void':
                return 0
            else:
                return 1
        elif ast.type in ('FunType', 'StructType', 'UnionType'):
            # TODO might be unboxed, all on stack, in future
            return 1
        else:
            raise NotImplementedError(ast)

    def get_label(self, pref):
        count = self.labels.get(pref, 0)
        label = '%s_%d' % (pref, count)
        self.labels[pref] = count + 1
        return label

    def get_tag(self, value):
        if value not in self.tags:
            self.tags[value] = self.tag_count
            self.tag_count += 1
        return self.tags[value]

    def compile(self, ast):
        if ast.type == 'Program':
            self.out.write("""\
; AUTOMATICALLY GENERATED -- EDIT AT OWN RISK

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
            save_argsize = self.fun_argsize
            self.fun_lit = self.get_label('fun_lit')
            self.local_pos = 1
            self.out.write('%s:\n' % self.fun_lit)
            # also saves the old baseptr right here
            self.out.write('set_baseptr\n')
            self.compile(ast.children[0])
            self.compile(ast.children[1])
            # TODO copy the result value(S) to the first arg position
            # (for now the opcode handles that)
            self.out.write('exeunt_%s:\n' % self.fun_lit)
            # base this on return type: void = 0, int = 1, union = 2, etc
            # TODO use size_of, when it works on types
            returnsize = 1
            if ast.aux.return_type == Void():
                returnsize = 0
            self.out.write('set_returnsize %d\n' % returnsize)
            self.out.write('clear_baseptr %d\n' % (0 - self.fun_argsize))
            self.out.write('rts\n')
            self.out.write('%s:\n' % past_fun)
            self.out.write('push %s\n' % self.fun_lit)
            self.fun_argsize = save_argsize
            self.fun_lit = save_fun
        elif ast.type == 'Args':
            argsize = 0
            for child in ast.children:
                assert child.type == 'Arg'
                argsize += self.size_of(child.children[0])
            self.fun_argsize = argsize
            # first arg passed is DEEPEST, so go backwards.
            pos = 0 - self.fun_argsize
            for child in ast.children:
                self.out.write('%s_local_%s=%d\n' %
                    (self.fun_lit, child.value, pos))
                pos += self.size_of(child.children[0])
        elif ast.type == 'Body':
            self.compile(ast.children[0])
            self.compile(ast.children[1])
        elif ast.type == 'VarDecls':
            for child in ast.children:
                self.compile(child)
        elif ast.type == 'VarDecl':
            self.compile(ast.children[0])
            self.out.write('%s_local_%s=%s\n' %
                (self.fun_lit, ast.value, self.local_pos))
            self.local_pos += 1
        elif ast.type == 'Block':
            for child in ast.children:
                self.compile(child)
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
            if ast.aux == 'global':
                self.out.write('builtin_%s\n' % ast.value)
            elif ast.aux == 'toplevel':
                self.out.write('get_global %s_index\n' % ast.value)
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
            self.out.write('jmp exeunt_%s\n' % self.fun_lit)
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
            # TODO store in the order defined in the struct?
            fields = {}
            for child in ast.children[1:]:
                fields[child.aux] = child   # FieldInit.aux = position in struct
            for position in sorted(fields):
                self.compile(fields[position])
            self.out.write('push %d\n' % (len(ast.children) - 1))
            self.out.write('make_struct\n')  # sigh
        elif ast.type == 'FieldInit':
            self.compile(ast.children[0])
        elif ast.type == 'Index':
            self.compile(ast.children[0])
            self.out.write('get_field %d\n' % ast.aux)
        elif ast.type == 'TypeCast':
            self.compile(ast.children[0])
            self.out.write('; tag with "%s"\n' % ast.aux)
            if ast.aux == 'void':
                # special case.  there is nothing on the stack
                self.out.write('push 0\n')
            tag = self.get_tag(ast.aux)
            self.out.write('tag %d\n' % tag)
        elif ast.type == 'TypeCase':
            end_typecase = self.get_label('end_typecase')
            self.compile(ast.children[0])
            self.out.write('dup\n')
            self.out.write('get_tag\n')
            tag = self.get_tag(ast.aux)
            self.out.write('push %d\n' % tag)
            self.out.write('eq\n')
            self.out.write('bzero %s\n' % end_typecase)
            # set the value to the untagged value of the value
            self.out.write('dup\n')
            self.out.write('get_value\n')
            assert ast.children[0].type == 'VarRef'
            self.out.write('set_local %s_local_%s\n' % (self.fun_lit, ast.children[0].value))
            
            self.compile(ast.children[2])
            # now restore the value, with what was saved on the stack
            self.out.write('dup\n')
            self.out.write('set_local %s_local_%s\n' % (self.fun_lit, ast.children[0].value))
            
            self.out.write('%s:\n' % end_typecase)
            self.out.write('pop 1\n')
        else:
            raise NotImplementedError(repr(ast))
