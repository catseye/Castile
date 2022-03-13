"""castile {options} program-file.castile

Interpreter/compiler for Castile, a programming language with union types.

"""

import sys

from argparse import ArgumentParser

from castile.parser import Parser
from castile.eval import Program
from castile.transformer import FunctionLifter
from castile.checker import TypeChecker
from castile import backends


def main(argv):
    argparser = ArgumentParser()

    argparser.add_argument('input_files', nargs='+', metavar='FILENAME', type=str,
        help='Source files containing the Castile program'
    )
    argparser.add_argument("-a", "--show-ast",
        action="store_true", dest="show_ast", default=False,
        help="show parsed AST instead of evaluating"
    )
    argparser.add_argument("-c", "--compile-to", metavar='BACKEND',
        dest="compile_to", default=None,
        help="compile to given backend code instead "
             "of evaluating directly (available backends: "
             "c, javascript, ruby, stackmac)"
    )
    argparser.add_argument("-p", "--parse-only",
        action="store_true", dest="parse_only",
        default=False,
        help="parse the input program only and exit"
    )
    argparser.add_argument("-Y", "--no-typecheck",
        action="store_false", dest="typecheck", default=True,
        help="do not typecheck the program"
    )
    argparser.add_argument('--version', action='version', version="%(prog)s 0.5")

    options = argparser.parse_args(argv[1:])

    with open(options.input_files[0], 'r') as f:
        p = Parser(f.read())
        ast = p.program()
        if options.show_ast:
            print(ast.pprint(0))
            print("-----")
        if options.parse_only:
            sys.exit(0)
        if options.typecheck:
            t = TypeChecker()
            t.collect_structs(ast)
            try:
                t.type_of(ast)
            except Exception:
                if options.show_ast:
                    print(ast.pprint(0))
                    print("-----")
                raise
        if options.compile_to is not None:
            x = FunctionLifter()
            ast = x.lift_functions(ast)
            if options.show_ast:
                print(ast.pprint(0))
                print("-----")
            c = getattr(backends, options.compile_to).Compiler(sys.stdout)
            c.compile(ast)
            sys.exit(0)
        e = Program()
        e.load(ast)
        r = e.run()
        if r is not None:
            print(repr(r))
