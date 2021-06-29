# nascent! embryonic! inchoate! alpha! wip!
from castile.types import *
from castile.transformer import VarDeclTypeAssigner

OPS = {
  'and': '&&',
  'or': '||',
}

PRELUDE = r"""
/* AUTOMATICALLY GENERATED -- EDIT AT OWN RISK */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef int CASTILE_VOID;

void print(char *s)
{
    printf("%s\n", s);
}

char *concat(char *s, char *t)
{
    char *st = malloc(strlen(s) + strlen(t) + 1);
    st[0] = '\0';
    strcat(st, s);
    strcat(st, t);
    return st;
}

char *substr(char *s, int p, int k)
{
    char *st = malloc(k + 1);
    int i;
    for (i = 0; i < k; i++) {
        st[i] = s[p+i];
    }
    st[i] = '\0';
    return st;
}

int len(char *s)
{
    return strlen(s);
}

struct tagged_value {
    int type;
    union {
        void *ptr;
        int i;
    };
};

struct tagged_value *tag(int type, void *value) {
}

"""


class Compiler(object):
    def __init__(self, out):
        self.out = out
        self.main_type = None
        self.indent = 0

    def commas(self, asts, sep=','):
        if asts:
            for child in asts[:-1]:
                self.compile(child)
                self.out.write(sep)
            self.compile(asts[-1])

    def write(self, x):
        self.out.write(x)

    def write_indent(self, x):
        self.out.write('  ' * self.indent)
        self.out.write(x)

    # as used in local variable declarations
    def c_type(self, type):
        if type == Integer():
            return 'int'
        elif type == String():
            return 'char *'
        elif type == Void():
            return 'CASTILE_VOID'
        elif type == Boolean():
            return 'int'
        elif isinstance(type, Struct):
            return 'struct %s *' % type.name
        elif isinstance(type, Function):
            return 'void *'
        elif isinstance(type, Union):
            # oh dear
            return 'void *'
        else:
            raise NotImplementedError(type)

    def c_decl(self, type, name, args=True):
        if isinstance(type, Function):
            s = ''
            s += self.c_type(type.return_type) 
            s += ' %s' % name
            if args:
                s += '('
                s += ', '.join([self.c_type(a) for a in type.arg_types])
                s += ')'
            return s
        else:
            return '%s %s' % (self.c_type(type), name)

    def compile_postlude(self):
        self.write(r"""

int main(int argc, char **argv)
{""")
        if self.main_type == Void():
            self.write(r"""
    castile_main();
""")
        if self.main_type == Integer():
            self.write(r"""
    int x = castile_main();
    printf("%d\n", x);
""")
        if self.main_type == Boolean():
            self.write(r"""
    int x = castile_main();
    printf("%s\n", x ? "True" : "False");
""")
        self.write(r"""
    return 0;
}

""")

    def compile(self, ast):
        if ast.tag == 'Program':
            g = VarDeclTypeAssigner()
            g.assign_types(ast)
            self.write(PRELUDE)
            for child in ast.children:
                self.compile(child)
            self.compile_postlude()
        elif ast.tag == 'Defn':
            thing = ast.children[0]
            name = ast.value
            if name == 'main':
                name = 'castile_main'
                self.main_type = thing.type.return_type
            if thing.tag == 'FunLit':
                self.write(self.c_decl(thing.type, name, args=False))
                self.compile(ast.children[0])
            else:
                self.write_indent('%s = ' % ast.value)
                self.compile(ast.children[0])
                self.write(';\n')
        elif ast.tag == 'Forward':
            self.write_indent('extern %s;\n' % self.c_decl(ast.children[0].type, ast.value))
        elif ast.tag == 'StructDefn':
            self.write_indent('struct %s {' % ast.value)
            self.indent += 1
            for child in ast.children:
                self.compile(child)
            self.indent -= 1
            self.write_indent('};\n')
        elif ast.tag == 'FieldDefn':
            self.write_indent('%s;\n' % self.c_decl(ast.children[0].type, ast.value))
        elif ast.tag == 'FunLit':
            self.write_indent('(')
            self.compile(ast.children[0])
            self.write(') {\n')
            self.indent += 1
            self.compile(ast.children[1])
            self.indent -= 1
            self.write_indent('}\n')
        elif ast.tag == 'Args':
            self.commas(ast.children)
        elif ast.tag == 'Arg':
            self.write('%s %s' % (self.c_type(ast.type), ast.value))
        elif ast.tag == 'Body':
            self.compile(ast.children[0])
            self.compile(ast.children[1])
        elif ast.tag == 'VarDecls':
            for child in ast.children:
                self.compile(child)
        elif ast.tag == 'VarDecl':
            self.write_indent('%s %s;\n' % (self.c_type(ast.type), ast.value))
        elif ast.tag == 'Block':
            self.write_indent('{\n')
            self.indent += 1
            for child in ast.children:
                self.compile(child)
                self.write(';\n')
            self.indent -= 1
            self.write_indent('}\n')
        elif ast.tag == 'While':
            self.write_indent('while (')
            self.compile(ast.children[0])
            self.write(')\n')
            self.indent += 1
            self.compile(ast.children[1])
            self.indent -= 1
        elif ast.tag == 'Op':
            self.write('(')
            self.compile(ast.children[0])
            self.write(' %s ' % OPS.get(ast.value, ast.value))
            self.compile(ast.children[1])
            self.write(')')
        elif ast.tag == 'VarRef':
            self.write(ast.value)
        elif ast.tag == 'FunCall':
            self.write("((")
            self.write(self.c_decl(ast.children[0].type, '(*)'))
            self.write(")")
            self.compile(ast.children[0])
            self.write(")")
            self.write('(')
            self.commas(ast.children[1:])
            self.write(')')
        elif ast.tag == 'If':
            self.write_indent('if (')
            self.compile(ast.children[0])
            self.write(')\n')
            if len(ast.children) == 3:  # if-else
                self.indent += 1
                self.compile(ast.children[1])
                self.indent -= 1
                self.write_indent('else\n')
                self.indent += 1
                self.compile(ast.children[2])
                self.indent -= 1
            else:  # just-if
                self.indent += 1
                self.compile(ast.children[1])
                self.indent -= 1
        elif ast.tag == 'Return':
            self.write_indent('return ')
            self.compile(ast.children[0])
        elif ast.tag == 'Break':
            self.write_indent('break')
        elif ast.tag == 'Not':
            self.write('!(')
            self.compile(ast.children[0])
            self.write(')')
        elif ast.tag == 'None':
            self.write('(CASTILE_VOID)0')
        elif ast.tag == 'BoolLit':
            if ast.value:
                self.write("1")
            else:
                self.write("0")
        elif ast.tag == 'IntLit':
            self.write(str(ast.value))
        elif ast.tag == 'StrLit':
            self.write('"%s"' % ast.value)
        elif ast.tag == 'Assignment':
            self.write_indent('')
            self.compile(ast.children[0])
            self.write(' = ')
            self.compile(ast.children[1])
        elif ast.tag == 'Make':
            self.write('&(struct %s){ ' % ast.type.name)
            self.commas(ast.children[1:])
            self.write(' }')
        elif ast.tag == 'FieldInit':
            self.commas(ast.children)
        elif ast.tag == 'Index':
            self.compile(ast.children[0])
            self.write('->%s' % ast.value)
        elif ast.tag == 'TypeCast':
            self.write('tag("%s",' % str(ast.children[0].type))
            self.compile(ast.children[0])
            self.write(')')
        elif ast.tag == 'TypeCase':
            self.write_indent('if (tag(')
            self.compile(ast.children[0])
            self.write(") == '%s') {" % str(ast.children[1].type))
            self.write('save=')
            self.compile(ast.children[0])
            self.write(';\n')
            self.compile(ast.children[0])
            self.write('=')
            self.compile(ast.children[0])
            self.write('[1]\n')
            self.compile(ast.children[2])
            self.compile(ast.children[0])
            self.write(' = save;\n')
        else:
            raise NotImplementedError(repr(ast))
