"""castile {options} program-file.castile

Interpreter/compiler for Castile, an unremarkable programming language.

"""

import sys

from optparse import OptionParser

from castile.parser import Parser
from castile.eval import Program
from castile.transformer import FunctionLifter
from castile.checker import TypeChecker
from castile import backends


def main(argv):
    optparser = OptionParser(__doc__.strip())
    optparser.add_option("-a", "--show-ast",
                         action="store_true", dest="show_ast", default=False,
                         help="show parsed AST instead of evaluating")
    optparser.add_option("-c", "--compile-to", metavar='BACKEND',
                         dest="compile_to", default=None,
                         help="compile to given backend code instead "
                              "of evaluating directly (available backends: "
                              "javascript, ruby, stackmac)")
    optparser.add_option("-p", "--parse-only",
                         action="store_true", dest="parse_only",
                         default=False,
                         help="parse the input program only and exit")
    optparser.add_option("-t", "--test",
                         action="store_true", dest="test", default=False,
                         help="run test cases and exit")
    optparser.add_option("-Y", "--no-typecheck",
                         action="store_false", dest="typecheck", default=True,
                         help="do not typecheck the program")
    (options, args) = optparser.parse_args(argv[1:])
    if options.test:
        import doctest
        (fails, something) = doctest.testmod()
        if fails == 0:
            print "All tests passed."
            sys.exit(0)
        else:
            sys.exit(1)
    with open(args[0], 'r') as f:
        p = Parser(f.read())
        ast = p.program()
        if options.show_ast:
            print ast.pprint(0)
            print "-----"
        if options.parse_only:
            sys.exit(0)
        if options.typecheck:
            t = TypeChecker()
            t.collect_structs(ast)
            t.type_of(ast)
        if options.compile_to is not None:
            x = FunctionLifter()
            ast = x.lift_functions(ast)
            if options.show_ast:
                print ast.pprint(0)
                print "-----"
            c = getattr(backends, options.compile_to).Compiler(sys.stdout)
            c.compile(ast)
            sys.exit(0)
        e = Program()
        e.load(ast)
        r = e.run()
        if r is not None:
            print repr(r)
