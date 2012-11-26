# nascent! embryonic! inchoate! alpha! wip!

OPS = {
}


class Compiler(object):
    def __init__(self, out):
        self.out = out

    def commas(self, asts, sep=','):
        if asts:
            for child in asts[:-1]:
                self.compile(child)
                self.out.write(sep)
            self.compile(asts[-1])

    def c_type(self, type):
        return 'int'

    def compile(self, ast):
        if ast.tag == 'Program':
            self.out.write(r"""
/* AUTOMATICALLY GENERATED -- EDIT AT OWN RISK */

#include <stdio.h>

void print(char *s)
{
  printf("%s\n", s);
}

""")
            for child in ast.children:
                self.compile(child)
            self.out.write(r"""

int main(int argc, char **argv)
{
    int x = castile_main();
    printf("%d\n", x);
    return 0;
}

""")
        elif ast.tag == 'Defn':
            thing = ast.children[0]
            name = ast.value
            if name == 'main':
                name = 'castile_main'
            if thing.tag == 'FunLit':
                self.out.write('%s %s' % (self.c_type(thing.type.return_type), name))
                self.compile(ast.children[0])
            else:
                self.out.write('%s = ' % ast.value)
                self.compile(ast.children[0])
                self.out.write(';\n')
        elif ast.tag == 'Forward':
            self.out.write('extern %s;\n' % ast.value)
        elif ast.tag == 'StructDefn':
            self.out.write('struct %s {}\n' % ast.value)
        elif ast.tag == 'FunLit':
            self.out.write('(')
            self.compile(ast.children[0])
            self.out.write(') {\n')
            self.compile(ast.children[1])
            self.out.write('}\n')
        elif ast.tag == 'Args':
            self.commas(ast.children)
        elif ast.tag == 'Arg':
            self.out.write(ast.value)
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
            self.out.write('nil')
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
            self.out.write('malloc()<--{')
            self.commas(ast.children[1:])
            self.out.write('}')
        elif ast.tag == 'FieldInit':
            self.out.write("'%s'," % ast.value)
            self.compile(ast.children[0])
        elif ast.tag == 'Index':
            self.compile(ast.children[0])
            self.out.write('["%s"]' % ast.value)
        elif ast.tag == 'TypeCast':
            self.out.write("['%s'," % str(ast.children[0].type))
            self.compile(ast.children[0])
            self.out.write(']')
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
