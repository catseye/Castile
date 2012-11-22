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
        if ast.type == 'Program':
            self.out.write("""\
/* AUTOMATICALLY GENERATED -- EDIT AT OWN RISK */

/*
var stdin = process.openStdin();
// node.js does not make this easy.  forgetting about it for now.
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
  } else if (typeof o === "object") {
    if (o._fieldnames === undefined) {
      var s = "(";
      for (var i = 0; i < o.length; i++) {
        s += repr(o[i]);
        if (i != o.length - 1) { s += ', '; }
      }
      s += ")";
      return s;
    } else {
      var s = "{";
      for (var i = 0; i < o._fieldnames.length; i++) {
        s += repr(o._fieldnames[i]);
        s += ': ';
        s += repr(o[o._fieldnames[i]]);
        if (i != o._fieldnames.length - 1) { s += ', '; }
      }
      s += "}";
      return s;
    }
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
        elif ast.type == 'Defn':
            self.out.write('%s = ' % ast.value)
            self.compile(ast.children[0])
            self.out.write(';\n')
        elif ast.type in ('StructDefn', 'Forward'):
            pass
        elif ast.type == 'FunLit':
            self.out.write('function(')
            self.compile(ast.children[0])
            self.out.write(')\n')
            self.compile(ast.children[1])
        elif ast.type == 'Args':
            self.commas(ast.children)
        elif ast.type == 'Arg':
            self.out.write(ast.value)
        elif ast.type == 'Block':
            self.out.write('{')
            for child in ast.children:
                self.compile(child)
                self.out.write(';\n')
            self.out.write('}')
        elif ast.type == 'VarDecl':
            self.out.write('var %s = ' % ast.value)
            self.compile(ast.children[0])
        elif ast.type == 'While':
            self.out.write('while (')
            self.compile(ast.children[0])
            self.out.write(')')
            self.compile(ast.children[1])
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
            self.out.write('(')
            self.commas(ast.children[1:])
            self.out.write(')')
        elif ast.type == 'If':
            self.out.write('if(')
            self.compile(ast.children[0])
            self.out.write(')')
            if len(ast.children) == 3:  # if-else
                self.compile(ast.children[1])
                self.out.write(' else ')
                self.compile(ast.children[2])
            else:  # just-if
                self.compile(ast.children[1])
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
            self.out.write('null')
        elif ast.type == 'IntLit':
            self.out.write(str(ast.value))
        elif ast.type == 'StrLit':
            self.out.write("'%s'" % ast.value)
        elif ast.type == 'BoolLit':
            if ast.value:
                self.out.write("true")
            else:
                self.out.write("false")
        elif ast.type == 'Assignment':
            self.compile(ast.children[0])
            self.out.write(' = ')
            self.compile(ast.children[1])
        elif ast.type == 'Make':
            self.out.write('{')
            self.commas(ast.children[1:])
            self.out.write(", '_fieldnames': [")
            for fieldinit in ast.children[1:-1]:
                self.out.write("'%s', " % fieldinit.value)
            self.out.write("'%s'" % ast.children[-1].value)
            self.out.write(']}')
        elif ast.type == 'FieldInit':
            self.out.write("'%s':" % ast.value)
            self.compile(ast.children[0])
        elif ast.type == 'Index':
            self.compile(ast.children[0])
            self.out.write('.%s' % ast.value)
        elif ast.type == 'TypeCast':
            self.out.write("['%s'," % ast.value)
            self.compile(ast.children[0])
            self.out.write(']')
        elif ast.type == 'TypeCase':
            self.out.write('if (')
            self.compile(ast.children[0])
            self.out.write("[0] == '%s')" % ast.value)
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
