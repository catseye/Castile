from castile.backends.base import BaseCompiler
from castile.types import Struct, Union

OPS = {
    'and': '&&',
    'or': '||',
    '==': '===',
}

PRELUDE = r"""
/* AUTOMATICALLY GENERATED -- EDIT AT YOUR OWN RISK */

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
var str = function(n) { return '' + n; };

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

var equal_tagged_value = function(tv1, tv2)
{
    return (tv1.tag === tv2.tag) && (tv1.value === tv2.value);
}
"""

POSTLUDE = """\

var result = main();
if (result !== undefined && result !== null)
  print(repr(result));
"""


class Compiler(BaseCompiler):

    def compile(self, ast):
        if ast.tag == 'Program':
            self.write(PRELUDE)
            for child in ast.children:
                self.compile(child)
            self.write(POSTLUDE)
        elif ast.tag == 'Defn':
            self.write('var %s = ' % ast.value)
            self.compile(ast.children[0])
            self.write(';\n')
        elif ast.tag == 'Forward':
            pass
        elif ast.tag == 'StructDefn':
            field_defns = ast.children[0].children
            self.write('function equal_%s(a, b) {\n' % ast.value)
            for child in field_defns:
                assert child.tag == 'FieldDefn', child.tag
                struct_type = child.children[0].value if child.children[0].tag == 'StructType' else None
                if struct_type:
                    self.write('if (!equal_%s(a.%s, b.%s)) return false;\n' % (struct_type, child.value, child.value))
                else:
                    self.write('if (a.%s !== b.%s) return false;\n' % (child.value, child.value))
            self.write('return true;\n')
            self.write('}\n\n')
        elif ast.tag == 'FunLit':
            self.write('function(')
            self.compile(ast.children[0])
            self.write(')\n')
            self.compile(ast.children[1])
        elif ast.tag == 'Args':
            self.commas(ast.children)
        elif ast.tag == 'Arg':
            self.write(ast.value)
        elif ast.tag == 'Body':
            self.write('{')
            self.compile(ast.children[0])
            assert ast.children[1].tag == 'Block'
            block = ast.children[1]
            for child in block.children:
                self.compile(child)
                self.write(';\n')
            self.write('}')
        elif ast.tag == 'VarDecls':
            for child in ast.children:
                self.compile(child)
        elif ast.tag == 'VarDecl':
            self.write('var %s;\n' % ast.value)
        elif ast.tag == 'Block':
            self.write('{')
            for child in ast.children:
                self.compile(child)
                self.write(';\n')
            self.write('}')
        elif ast.tag == 'While':
            self.write('while (')
            self.compile(ast.children[0])
            self.write(')')
            self.compile(ast.children[1])
        elif ast.tag == 'Op':
            if ast.value == '==' and isinstance(ast.children[0].type, Struct):
                self.write('equal_%s(' % ast.children[0].type.name)
                self.compile(ast.children[0])
                self.write(', ')
                self.compile(ast.children[1])
                self.write(')')
            elif ast.value == '==' and isinstance(ast.children[0].type, Union):
                self.write('equal_tagged_value(')
                self.compile(ast.children[0])
                self.write(', ')
                self.compile(ast.children[1])
                self.write(')')
            else:
                self.write('(')
                self.compile(ast.children[0])
                self.write(' %s ' % OPS.get(ast.value, ast.value))
                self.compile(ast.children[1])
                self.write(')')
        elif ast.tag == 'VarRef':
            self.write(ast.value)
        elif ast.tag == 'FunCall':
            self.compile(ast.children[0])
            self.write('(')
            self.commas(ast.children[1:])
            self.write(')')
        elif ast.tag == 'If':
            self.write('if(')
            self.compile(ast.children[0])
            self.write(')')
            if len(ast.children) == 3:  # if-else
                self.compile(ast.children[1])
                self.write(' else ')
                self.compile(ast.children[2])
            else:  # just-if
                self.compile(ast.children[1])
        elif ast.tag == 'Return':
            self.write('return ')
            self.compile(ast.children[0])
        elif ast.tag == 'Break':
            self.write('break')
        elif ast.tag == 'Not':
            self.write('!(')
            self.compile(ast.children[0])
            self.write(')')
        elif ast.tag == 'None':
            self.write('null')
        elif ast.tag == 'IntLit':
            self.write(str(ast.value))
        elif ast.tag == 'StrLit':
            self.write("'%s'" % ast.value)
        elif ast.tag == 'BoolLit':
            if ast.value:
                self.write("true")
            else:
                self.write("false")
        elif ast.tag == 'Assignment':
            self.compile(ast.children[0])
            self.write(' = ')
            self.compile(ast.children[1])
        elif ast.tag == 'Make':
            self.write('{')
            self.commas(ast.children[1:])
            self.write('}')
        elif ast.tag == 'FieldInit':
            self.write("'%s':" % ast.value)
            self.compile(ast.children[0])
        elif ast.tag == 'Index':
            self.compile(ast.children[0])
            self.write('.%s' % ast.value)
        elif ast.tag == 'TypeCast':
            self.write("['%s'," % str(ast.children[0].type))
            self.compile(ast.children[0])
            self.write(']')
        elif ast.tag == 'TypeCase':
            self.write('if (')
            self.compile(ast.children[0])
            self.write("[0] == '%s')" % str(ast.children[1].type))
            self.write('{ var save=')
            self.compile(ast.children[0])
            self.write('; ')
            self.compile(ast.children[0])
            self.write('=')
            self.compile(ast.children[0])
            self.write('[1]; ')
            self.compile(ast.children[2])
            self.compile(ast.children[0])
            self.write(' =save; }')
        else:
            raise NotImplementedError(repr(ast))
