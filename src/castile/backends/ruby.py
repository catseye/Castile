OPS = {
}

PRELUDE = """\
# AUTOMATICALLY GENERATED -- EDIT AT OWN RISK

input = lambda { |s|
  print(s)
  STDIN.gets.chomp
}

print = lambda { |s|
  puts s
}

read = lambda { |n|
  s = STDIN.read(n)
  if s == nil then s = "" end
  return s
}

write = lambda { |s|
  STDOUT.write(s)
}

len = lambda { |s|
  s.length
}

concat = lambda { |s1, s2|
  s1 + s2
}

substr = lambda { |s, p, k|
  s[p..p+(k-1)]
}

str = lambda { |n|
  n.to_s
}

def repr o
  if o == true
    return "True"
  elsif o == false
    return "False"
  elsif o == nil
    return "None"
  elsif o.is_a? String
    return "'" + o + "'"
  else
    return o.to_s
  end
end

"""

POSTLUDE = """\

result = main.call()
if result != nil
  puts(repr(result))
end
"""


class Compiler(object):
    def __init__(self, out):
        self.out = out
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

    def mangle(self, ident):
        if ident.startswith('next'):
            return '{}_'.format(ident)
        return ident

    def compile(self, ast):
        if ast.tag == 'Program':
            self.write(PRELUDE)
            for child in ast.children:
                self.compile(child)
            self.write(POSTLUDE)
        elif ast.tag == 'Defn':
            self.write_indent('%s = ' % ast.value)
            self.compile(ast.children[0])
            self.write('\n')
        elif ast.tag == 'Forward':
            self.write_indent('%s = nil\n' % ast.value)
        elif ast.tag == 'StructDefn':
            pass
        elif ast.tag == 'FunLit':
            self.write_indent('lambda { |')
            self.compile(ast.children[0])
            self.write('|\n')
            self.indent += 1
            self.compile(ast.children[1])
            self.write_indent('return nil\n')
            self.indent -= 1
            self.write_indent('}\n')
        elif ast.tag == 'Args':
            self.commas(ast.children)
        elif ast.tag == 'Arg':
            self.write(ast.value)
        elif ast.tag == 'Body':
            self.compile(ast.children[0])
            self.compile(ast.children[1])
        elif ast.tag == 'VarDecls':
            for child in ast.children:
                self.compile(child)
        elif ast.tag == 'VarDecl':
            self.write_indent('%s = nil;\n' % self.mangle(ast.value))
        elif ast.tag == 'Block':
            for child in ast.children:
                self.compile(child)
                self.write('\n')
        elif ast.tag == 'While':
            self.write_indent('while (')
            self.compile(ast.children[0])
            self.write(') do\n')
            self.indent += 1
            self.compile(ast.children[1])
            self.indent -= 1
            self.write_indent('end\n')
        elif ast.tag == 'Op':
            self.write('(')
            self.compile(ast.children[0])
            self.write(' %s ' % OPS.get(ast.value, ast.value))
            self.compile(ast.children[1])
            self.write(')')
        elif ast.tag == 'VarRef':
            self.write(self.mangle(ast.value))
        elif ast.tag == 'FunCall':
            self.compile(ast.children[0])
            self.write('.call(')
            self.commas(ast.children[1:])
            self.write(')')
        elif ast.tag == 'If':
            self.write_indent('if (')
            self.compile(ast.children[0])
            self.write(') then\n')
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
            self.write_indent('end\n')
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
            self.write('nil')
        elif ast.tag == 'BoolLit':
            if ast.value:
                self.write("true")
            else:
                self.write("false")
        elif ast.tag == 'IntLit':
            self.write(str(ast.value))
        elif ast.tag == 'StrLit':
            self.write("'%s'" % ast.value)
        elif ast.tag == 'Assignment':
            self.write_indent('')
            self.compile(ast.children[0])
            self.write(' = ')
            self.compile(ast.children[1])
        elif ast.tag == 'Make':
            self.write('{')
            self.commas(ast.children[1:])
            self.write('}')
        elif ast.tag == 'FieldInit':
            self.write("'%s'=>" % ast.value)
            self.compile(ast.children[0])
        elif ast.tag == 'Index':
            self.compile(ast.children[0])
            self.write('["%s"]' % ast.value)
        elif ast.tag == 'TypeCast':
            self.write("['%s'," % str(ast.children[0].type))
            self.compile(ast.children[0])
            self.write(']')
        elif ast.tag == 'TypeCase':
            self.write_indent('if (')
            self.compile(ast.children[0])
            self.write("[0] == '%s')" % str(ast.children[1].type))
            self.write('then save=')
            self.compile(ast.children[0])
            self.write('\n')
            self.compile(ast.children[0])
            self.write('=')
            self.compile(ast.children[0])
            self.write('[1]\n')
            self.compile(ast.children[2])
            self.compile(ast.children[0])
            self.write(' = save end')
        else:
            raise NotImplementedError(repr(ast))
