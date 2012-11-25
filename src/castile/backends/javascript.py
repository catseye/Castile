OPS = {
    'and': '&&',
    'or': '||',
    '==': '===',
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
/* AUTOMATICALLY GENERATED -- EDIT AT OWN RISK */

/*
var stdin = process.openStdin();
// node.js does not make this easy -- not unless I want to
// generate code in cps!  forgetting about it for now.
var input = function(s) {
  var answer = undefined;
  stdin.on('data', function(chunk) { answer = chunk; });
  return answer;
};
*/

var print = function(s) { console.log(s); };
var len = function(s) { return s.length; };
var concat = function(s1,s2) { return s1 + s2; };
var substr = function(s,p,k) { return s.substr(p, k); };

var repr = function(o) {
  if (typeof o === "string") {
    return "'" + o + "'";
  } else if (o === true) {
    return "True";
  } else if (o === false) {
    return "False";
  } else if (o === undefined) {
    return "";
  } else if (o === null) {
    return "None";
  } else {
    return o;
  }
};

""")
            for child in ast.children:
                self.compile(child)
            self.out.write("""\

var result = main();
if (result !== undefined && result !== null)
  print(repr(result));
""")
        elif ast.tag == 'Defn':
            self.out.write('%s = ' % ast.value)
            self.compile(ast.children[0])
            self.out.write(';\n')
        elif ast.tag in ('StructDefn', 'Forward'):
            pass
        elif ast.tag == 'FunLit':
            self.out.write('function(')
            self.compile(ast.children[0])
            self.out.write(')\n')
            self.compile(ast.children[1])
        elif ast.tag == 'Args':
            self.commas(ast.children)
        elif ast.tag == 'Arg':
            self.out.write(ast.value)
        elif ast.tag == 'Body':
            self.out.write('{')
            self.compile(ast.children[0])
            assert ast.children[1].tag == 'Block'
            block = ast.children[1]
            for child in block.children:
                self.compile(child)
                self.out.write(';\n')
            self.out.write('}')
        elif ast.tag == 'VarDecls':
            for child in ast.children:
                self.compile(child)
        elif ast.tag == 'VarDecl':
            self.out.write('%s = ' % ast.value)
            self.compile(ast.children[0])
            self.out.write(';\n')
        elif ast.tag == 'Block':
            self.out.write('{')
            for child in ast.children:
                self.compile(child)
                self.out.write(';\n')
            self.out.write('}')
        elif ast.tag == 'While':
            self.out.write('while (')
            self.compile(ast.children[0])
            self.out.write(')')
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
            self.out.write('if(')
            self.compile(ast.children[0])
            self.out.write(')')
            if len(ast.children) == 3:  # if-else
                self.compile(ast.children[1])
                self.out.write(' else ')
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
            self.out.write('null')
        elif ast.tag == 'IntLit':
            self.out.write(str(ast.value))
        elif ast.tag == 'StrLit':
            self.out.write("'%s'" % ast.value)
        elif ast.tag == 'BoolLit':
            if ast.value:
                self.out.write("true")
            else:
                self.out.write("false")
        elif ast.tag == 'Assignment':
            self.compile(ast.children[0])
            self.out.write(' = ')
            self.compile(ast.children[1])
        elif ast.tag == 'Make':
            self.out.write('{')
            self.commas(ast.children[1:])
            self.out.write('}')
        elif ast.tag == 'FieldInit':
            self.out.write("'%s':" % ast.value)
            self.compile(ast.children[0])
        elif ast.tag == 'Index':
            self.compile(ast.children[0])
            self.out.write('.%s' % ast.value)
        elif ast.tag == 'TypeCast':
            self.out.write("['%s'," % ast.aux)
            self.compile(ast.children[0])
            self.out.write(']')
        elif ast.tag == 'TypeCase':
            self.out.write('if (')
            self.compile(ast.children[0])
            self.out.write("[0] == '%s')" % ast.aux)
            self.out.write('{ var save=')
            self.compile(ast.children[0])
            self.out.write('; ')
            self.compile(ast.children[0])
            self.out.write('=')
            self.compile(ast.children[0])
            self.out.write('[1]; ')
            self.compile(ast.children[2])
            self.compile(ast.children[0])
            self.out.write(' =save; }')
        else:
            raise NotImplementedError(repr(ast))
