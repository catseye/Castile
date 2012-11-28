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
            #s = '/* {CTYPE %s */' % type
            s = '('
            s += self.c_type(type.return_type) + ' (*)('
            s += ', '.join([self.c_type(a) for a in type.arg_types])
            s += '))'
            #s += '/* }CTYPE */'
            return s
        elif isinstance(type, Union):
            # oh dear
            return 'void *'
        else:
            raise NotImplementedError(type)

    def c_decl(self, type, name, ptr=False, args=False):
        if type == Integer():
            return 'int %s' % name
        elif type == String():
            return 'char * %s' % name
        elif type == Void():
            return 'void %s' % name
        elif type == Boolean():
            return 'int %s' % name
        elif isinstance(type, Struct):
            return 'struct %s * %s' % (type.name, name)
        elif isinstance(type, Function):
            #s = '/* {CDECL %s */' % type
            s = ''
            s += self.c_type(type.return_type) 
            if ptr:
                s += ' (*%s)' % name
            else:
                s += ' %s' % name
            if args:
                s += '('
                s += ', '.join([self.c_type(a) for a in type.arg_types])
                s += ')'
            #s += '/* }CDECL */'
            return s
        elif isinstance(type, Union):
            # oh dear
            return 'void * %s' % name
        else:
            raise NotImplementedError(type)

    def compile(self, ast):
        if ast.tag == 'Program':
            g = VarDeclTypeAssigner()
            g.assign_types(ast)
            self.out.write(r"""
/* AUTOMATICALLY GENERATED -- EDIT AT OWN RISK */

#include <stdio.h>
#include <stdlib.h>

void print(char *s)
{
  printf("%s\n", s);
}

struct tagged_value {
    int type;
    union {
        void *ptr;
        int i;
    };
};

/*
struct tagged_value *tag(char *, void *) {
}
*/
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
            self.out.write('extern %s;\n' % self.c_decl(ast.children[0].type, ast.value, args=True))
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
            self.out.write(self.c_decl(ast.type, ast.value))
        elif ast.tag == 'Body':
            self.compile(ast.children[0])
            self.compile(ast.children[1])
        elif ast.tag == 'VarDecls':
            for child in ast.children:
                self.compile(child)
        elif ast.tag == 'VarDecl':
            self.out.write('%s;\n' % self.c_decl(ast.type, ast.value, ptr=True, args=True))
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
            self.compile(ast.children[0])
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
            self.out.write('if (')
            self.compile(ast.children[0])
            self.out.write("[0] == '%s')" % str(ast.children[1].type))
            self.out.write('then save=')
            self.compile(ast.children[0])
            self.out.write('\n')
            self.compile(ast.children[0])
            self.out.write('=')
            self.compile(ast.children[0])
            self.out.write('[1]\n')
            self.compile(ast.children[2])
            self.compile(ast.children[0])
            self.out.write(' = save end')
        else:
            raise NotImplementedError(repr(ast))
