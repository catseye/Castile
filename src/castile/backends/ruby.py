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
        if ast.type == 'Program':
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
  elsif o.is_a? Array
    if o.length == 0 then return "()" end
    h = "("
    for c in o[0..o.length-2] do
      h += repr(c) + ", "
    end
    return h + repr(o[o.length-1]) + ")"
  elsif o.is_a? Hash
      s = "{"
      fn = o["_fieldnames"]
      for field in fn[0..fn.length-2] do
        s += repr(field) + ": " + repr(o[field]) + ", "
      end
      s += repr(fn[fn.length-1]) + ": " + repr(o[fn[fn.length-1]])
      s += "}"
      return s
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
        elif ast.type == 'Defn':
            self.out.write('%s = ' % ast.value)
            self.compile(ast.children[0])
            self.out.write('\n')
        elif ast.type in ('Forward'):
            self.out.write('%s = nil\n' % ast.value)
        elif ast.type in ('StructDefn'):
            pass
        elif ast.type == 'FunLit':
            self.out.write('lambda { |')
            self.compile(ast.children[0])
            self.out.write('|\n')
            self.compile(ast.children[1])
            self.out.write('return nil }')
        elif ast.type == 'Args':
            self.commas(ast.children)
        elif ast.type == 'Arg':
            self.out.write(ast.value)
        elif ast.type == 'Block':
            for child in ast.children:
                self.compile(child)
                self.out.write('\n')
        elif ast.type == 'VarDecl':
            self.out.write('%s = ' % ast.value)
            self.compile(ast.children[0])
        elif ast.type == 'While':
            self.out.write('while (')
            self.compile(ast.children[0])
            self.out.write(') do\n')
            self.compile(ast.children[1])
            self.out.write('end\n')
        elif ast.type == 'Op':
            self.out.write('(')
            self.compile(ast.children[0])
            self.out.write(' %s ' % OPS.get(ast.value, ast.value))
            self.compile(ast.children[1])
            self.out.write(')')
        elif ast.type == 'VarRef':
            self.out.write(ast.value)
        elif ast.type == 'FunCall':
            self.compile(ast.children[0])
            self.out.write('.call(')
            self.commas(ast.children[1:])
            self.out.write(')')
        elif ast.type == 'If':
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
        elif ast.type == 'Return':
            self.out.write('return ')
            self.compile(ast.children[0])
        elif ast.type == 'Break':
            self.out.write('break')
        elif ast.type == 'Not':
            self.out.write('!(')
            self.compile(ast.children[0])
            self.out.write(')')
        elif ast.type == 'None':
            self.out.write('nil')
        elif ast.type == 'BoolLit':
            if ast.value:
                self.out.write("true")
            else:
                self.out.write("false")
        elif ast.type == 'IntLit':
            self.out.write(str(ast.value))
        elif ast.type == 'StrLit':
            self.out.write("'%s'" % ast.value)
        elif ast.type == 'Assignment':
            self.compile(ast.children[0])
            self.out.write(' = ')
            self.compile(ast.children[1])
        elif ast.type == 'Make':
            self.out.write('{')
            self.commas(ast.children[1:])
            self.out.write(", '_fieldnames', [")
            for fieldinit in ast.children[1:-1]:
                self.out.write("'%s', " % fieldinit.value)
            self.out.write("'%s'" % ast.children[-1].value)
            self.out.write(']}')
        elif ast.type == 'FieldInit':
            self.out.write("'%s'," % ast.value)
            self.compile(ast.children[0])
        elif ast.type == 'Index':
            self.compile(ast.children[0])
            self.out.write('["%s"]' % ast.value)
        elif ast.type == 'TypeCast':
            self.out.write("['%s'," % ast.value)
            self.compile(ast.children[0])
            self.out.write(']')
        elif ast.type == 'TypeCase':
            self.out.write('if (')
            self.compile(ast.children[0])
            self.out.write("[0] == '%s')" % ast.value)
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
