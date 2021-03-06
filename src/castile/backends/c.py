# nascent! embryonic! inchoate! alpha! wip!
from castile.types import *
from castile.transformer import VarDeclTypeAssigner

OPS = {
  'and': '&&',
  'or': '||',
}


class Compiler(object):
    def __init__(self, out):
        self.out = out
        self.main_type = None

    def commas(self, asts, sep=','):
        if asts:
            for child in asts[:-1]:
                self.compile(child)
                self.out.write(sep)
            self.compile(asts[-1])

    # as used in local variable declarations
    def c_type(self, type):
        if type == Integer():
            return 'int'
        elif type == String():
            return 'char *'
        elif type == Void():
            return 'void'
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

    def compile(self, ast):
        if ast.tag == 'Program':
            g = VarDeclTypeAssigner()
            g.assign_types(ast)
            self.out.write(r"""
/* AUTOMATICALLY GENERATED -- EDIT AT OWN RISK */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

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

struct tagged_value {
    int type;
    union {
        void *ptr;
        int i;
    };
};

struct tagged_value *tag(int type, void *value) {
}

""")
            for child in ast.children:
                self.compile(child)
            if self.main_type == Void():
                self.out.write(r"""

int main(int argc, char **argv)
{
    castile_main();
    return 0;
}

""")
            if self.main_type == Integer():
                self.out.write(r"""

int main(int argc, char **argv)
{
    int x = castile_main();
    printf("%d\n", x);
    return 0;
}

""")
            if self.main_type == Boolean():
                self.out.write(r"""

int main(int argc, char **argv)
{
    int x = castile_main();
    printf("%s\n", x ? "True" : "False");
    return 0;
}

""")
        elif ast.tag == 'Defn':
            thing = ast.children[0]
            name = ast.value
            if name == 'main':
                name = 'castile_main'
                self.main_type = thing.type.return_type
            if thing.tag == 'FunLit':
                self.out.write(self.c_decl(thing.type, name, args=False))
                self.compile(ast.children[0])
            else:
                self.out.write('%s = ' % ast.value)
                self.compile(ast.children[0])
                self.out.write(';\n')
        elif ast.tag == 'Forward':
            self.out.write('extern %s;\n' % self.c_decl(ast.children[0].type, ast.value))
        elif ast.tag == 'StructDefn':
            self.out.write('struct %s {' % ast.value)
            for child in ast.children:
                self.compile(child)
            self.out.write('};\n')
        elif ast.tag == 'FieldDefn':
            self.out.write('%s;\n' % self.c_decl(ast.children[0].type, ast.value))
        elif ast.tag == 'FunLit':
            self.out.write('(')
            self.compile(ast.children[0])
            self.out.write(') {\n')
            self.compile(ast.children[1])
            self.out.write('}\n')
        elif ast.tag == 'Args':
            self.commas(ast.children)
        elif ast.tag == 'Arg':
            self.out.write('%s %s' % (self.c_type(ast.type), ast.value))
        elif ast.tag == 'Body':
            self.compile(ast.children[0])
            self.compile(ast.children[1])
        elif ast.tag == 'VarDecls':
            for child in ast.children:
                self.compile(child)
        elif ast.tag == 'VarDecl':
            self.out.write('%s %s;\n' % (self.c_type(ast.type), ast.value))
        elif ast.tag == 'Block':
            self.out.write('{\n')
            for child in ast.children:
                self.compile(child)
                self.out.write(';\n')
            self.out.write('}\n')
        elif ast.tag == 'While':
            self.out.write('while (')
            self.compile(ast.children[0])
            self.out.write(')\n')
            self.compile(ast.children[1])
        elif ast.tag == 'Op':
            self.out.write('(')
            self.compile(ast.children[0])
            self.out.write(' %s ' % OPS.get(ast.value, ast.value))
            self.compile(ast.children[1])
            self.out.write(')')
        elif ast.tag == 'VarRef':
            self.out.write(ast.value)
        elif ast.tag == 'FunCall':
            self.out.write("((")
            self.out.write(self.c_decl(ast.children[0].type, '(*)'))
            self.out.write(")")
            self.compile(ast.children[0])
            self.out.write(")")
            self.out.write('(')
            self.commas(ast.children[1:])
            self.out.write(')')
        elif ast.tag == 'If':
            self.out.write('if (')
            self.compile(ast.children[0])
            self.out.write(')\n')
            if len(ast.children) == 3:  # if-else
                self.compile(ast.children[1])
                self.out.write(' else\n')
                self.compile(ast.children[2])
            else:  # just-if
                self.compile(ast.children[1])
        elif ast.tag == 'Return':
            self.out.write('return ')
            self.compile(ast.children[0])
        elif ast.tag == 'Break':
            self.out.write('break')
        elif ast.tag == 'Not':
            self.out.write('!(')
            self.compile(ast.children[0])
            self.out.write(')')
        elif ast.tag == 'None':
            self.out.write('')
        elif ast.tag == 'BoolLit':
            if ast.value:
                self.out.write("1")
            else:
                self.out.write("0")
        elif ast.tag == 'IntLit':
            self.out.write(str(ast.value))
        elif ast.tag == 'StrLit':
            self.out.write('"%s"' % ast.value)
        elif ast.tag == 'Assignment':
            self.compile(ast.children[0])
            self.out.write(' = ')
            self.compile(ast.children[1])
        elif ast.tag == 'Make':
            self.out.write('&(struct %s){ ' % ast.type.name)
            self.commas(ast.children[1:])
            self.out.write(' }')
        elif ast.tag == 'FieldInit':
            self.commas(ast.children)
        elif ast.tag == 'Index':
            self.compile(ast.children[0])
            self.out.write('->%s' % ast.value)
        elif ast.tag == 'TypeCast':
            self.out.write('tag("%s",' % str(ast.children[0].type))
            self.compile(ast.children[0])
            self.out.write(')')
        elif ast.tag == 'TypeCase':
            self.out.write('if (tag(')
            self.compile(ast.children[0])
            self.out.write(") == '%s') {" % str(ast.children[1].type))
            self.out.write('save=')
            self.compile(ast.children[0])
            self.out.write(';\n')
            self.compile(ast.children[0])
            self.out.write('=')
            self.compile(ast.children[0])
            self.out.write('[1]\n')
            self.compile(ast.children[2])
            self.compile(ast.children[0])
            self.out.write(' = save;\n')
        else:
            raise NotImplementedError(repr(ast))
