"""General AST manipulations:

*   bring all function definitions up to the toplevel
    (for languages like C)

TODO:

*   rearrange all toplevels so that non-function defns come before function defns.
*   rename all occurrences of a local variable (for the following)
*   bring all variable declarations up to the function body block
    (this may require renaming; the same name may be used in two non-nested blocks)
"""

from castile.ast import AST

class Transformer(object):
    def __init__(self):
        self.lifted_functions = []
        self.count = 0

    def make_name(self):
        self.count += 1
        return 'lifted_function%d' % self.count

    def lift_functions(self, ast):
        if ast.type == 'Program':
            children = []
            for child in ast.children:
                children.append(self.lift_functions(child))
            lifted_defns = []
            for (name, lf) in self.lifted_functions:
                lifted_defns.append(AST('Defn', [lf], value=name))
            return AST(ast.type, lifted_defns + children, value=ast.value)
        elif ast.type == 'Defn':
            # skip toplevel funlits; they don't have to be lifted.
            children = []
            for child in ast.children:
                if child.type == 'FunLit':
                    grandchildren = []
                    for grandchild in child.children:
                        grandchildren.append(self.lift_functions(grandchild))
                    children.append(AST('FunLit', grandchildren, value=child.value))
                else:
                    children.append(self.lift_functions(child))
            return AST(ast.type, children, value=ast.value)
        elif ast.type == 'FunLit':
            children = []
            for child in ast.children:
                children.append(self.lift_functions(child))
            new_ast = AST(ast.type, children, value=ast.value)
            name = self.make_name()
            self.lifted_functions.append((name, new_ast))
            return AST('VarRef', value=name)
        else:
            children = []
            for child in ast.children:
                children.append(self.lift_functions(child))
            return AST(ast.type, children, value=ast.value)
