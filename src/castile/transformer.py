"""General AST manipulations.

"""

from castile.ast import AST


class FunctionLifter(object):
    """Bring all function definitions up to the toplevel (for target
    languages like C).

    """
    def __init__(self):
        self.lifted_functions = []
        self.count = 0

    def make_name(self):
        self.count += 1
        return 'lifted_function%d' % self.count

    def lift_functions(self, ast):
        if ast.tag == 'Program':
            children = []
            for child in ast.children:
                children.append(self.lift_functions(child))
            lifted_defns = []
            for (name, lf) in self.lifted_functions:
                lifted_defns.append(AST('Defn', [lf], value=name))
            # rearrange toplevels so that non-function defns come
            # before function defns
            non_fun_defns = []
            non_lifted_defns = []
            for child in children:
                if child.children:
                    if child.children[0].tag == 'FunLit':
                        non_lifted_defns.append(child)
                    else:
                        non_fun_defns.append(child)
                else:
                    non_fun_defns.append(child)
            children = non_fun_defns + lifted_defns + non_lifted_defns
            return ast.copy(children=children)
        elif ast.tag == 'Defn':
            # skip toplevel funlits; they don't have to be lifted.
            children = []
            for child in ast.children:
                if child.tag == 'FunLit':
                    grandchildren = []
                    for grandchild in child.children:
                        grandchildren.append(self.lift_functions(grandchild))
                    children.append(child.copy(children=grandchildren))
                else:
                    children.append(self.lift_functions(child))
            return ast.copy(children=children)
        elif ast.tag == 'FunLit':
            children = []
            for child in ast.children:
                children.append(self.lift_functions(child))
            name = self.make_name()
            self.lifted_functions.append((name, ast.copy(children=children)))
            return AST('VarRef', value=name, type=ast.type, aux='toplevel')
        else:
            children = []
            for child in ast.children:
                children.append(self.lift_functions(child))
            return ast.copy(children=children)


class VarDeclTypeAssigner(object):
    def __init__(self):
        self.current_funlit = None

    def find_vardecl(self, name):
        body = self.current_funlit.children[1]
        assert body.tag == 'Body'
        vardecls = body.children[0]
        assert vardecls.tag == 'VarDecls'
        for child in vardecls.children:
            if child.value == name:
                return child

    def assign_types(self, ast):
        if ast.tag == 'FunLit':
            save = self.current_funlit
            self.current_funlit = ast
            for child in ast.children:
                self.assign_types(child)
            self.current_funlit = save
        elif ast.tag == 'Assignment':
            if ast.aux == 'defining instance':
                vardecl = self.find_vardecl(ast.children[0].value)
                vardecl.type = ast.children[1].type
            for child in ast.children:
                self.assign_types(child)
        else:
            for child in ast.children:
                self.assign_types(child)
