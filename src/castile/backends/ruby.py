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

    def compile(self, ast):
        if ast.tag == 'Program':
            self.out.write("""\
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

""")
            for child in ast.children:
                self.compile(child)
            self.out.write("""\

result = main.call()
if result != nil
  puts(repr(result))
end
""")
        elif ast.tag == 'Defn':
            self.out.write('%s = ' % ast.value)
            self.compile(ast.children[0])
            self.out.write('\n')
        elif ast.tag == 'Forward':
            self.out.write('%s = nil\n' % ast.value)
        elif ast.tag == 'StructDefn':
            pass
        elif ast.tag == 'FunLit':
            self.out.write('lambda { |')
            self.compile(ast.children[0])
            self.out.write('|\n')
            self.compile(ast.children[1])
            self.out.write('return nil }')
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
            self.out.write('%s = nil;\n' % ast.value)
        elif ast.tag == 'Block':
            for child in ast.children:
                self.compile(child)
                self.out.write('\n')
        elif ast.tag == 'While':
            self.out.write('while (')
            self.compile(ast.children[0])
            self.out.write(') do\n')
            self.compile(ast.children[1])
            self.out.write('end\n')
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
            self.out.write('.call(')
            self.commas(ast.children[1:])
            self.out.write(')')
        elif ast.tag == 'If':
            self.out.write('if (')
            self.compile(ast.children[0])
            self.out.write(') then\n')
            if len(ast.children) == 3:  # if-else
                self.compile(ast.children[1])
                self.out.write(' else\n')
                self.compile(ast.children[2])
            else:  # just-if
                self.compile(ast.children[1])
            self.out.write('end\n')
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
                self.out.write("true")
            else:
                self.out.write("false")
        elif ast.tag == 'IntLit':
            self.out.write(str(ast.value))
        elif ast.tag == 'StrLit':
            self.out.write("'%s'" % ast.value)
        elif ast.tag == 'Assignment':
            self.compile(ast.children[0])
            self.out.write(' = ')
            self.compile(ast.children[1])
        elif ast.tag == 'Make':
            self.out.write('{')
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
