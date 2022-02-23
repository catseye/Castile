from castile.ast import AST
from castile.scanner import Scanner, CastileSyntaxError


class Parser(object):
    """Parse a Castile program into an AST.

    The parser mainly just constructs the AST.  It does few other analyses
    or transformations itself.  However, there are a few:

    * It inserts a final `return` in a block where the last statement is a
      non-void expression.
    * It collects all assigned-to variable names in a function body, and
      turns them into VarDecl nodes.

    """
    def __init__(self, text):
        self.scanner = Scanner(text)
        self.locals = None

    ### Delegate to scanner

    def consume(self, *args, **kwargs):
        return self.scanner.consume(*args, **kwargs)

    def consume_type(self, *args, **kwargs):
        return self.scanner.consume_type(*args, **kwargs)

    def expect(self, *args, **kwargs):
        return self.scanner.expect(*args, **kwargs)

    def expect_type(self, *args, **kwargs):
        return self.scanner.expect_type(*args, **kwargs)

    def on(self, *args, **kwargs):
        return self.scanner.on(*args, **kwargs)

    def on_any(self, *args, **kwargs):
        return self.scanner.on_any(*args, **kwargs)

    def on_type(self, *args, **kwargs):
        return self.scanner.on_type(*args, **kwargs)

    ### Delegate to AST

    def ast(self, *args, **kwargs):
        kwargs['line'] = self.scanner.line
        return AST(*args, **kwargs)

    ### Parser proper

    def program(self):
        defns = []
        while not self.on_type('EOF'):
            defns.append(self.defn())
            self.consume(';')
        return self.ast('Program', defns)

    def defn(self):
        if self.consume('fun'):
            id = self.expect_type('identifier')
            self.expect("(")
            args = []
            if not self.on(")"):
                args.append(self.arg())
                while self.consume(","):
                    args.append(self.arg())
            self.expect(")")
            body = self.body()
            funlit = self.ast('FunLit', [self.ast('Args', args), body])
            return self.ast('Defn', [funlit], value=id)
        elif self.consume('struct'):
            id = self.expect_type('identifier')
            self.expect("{")
            components = []
            while not self.on('}'):
                name = self.expect_type('identifier')
                self.expect(':')
                texpr = self.texpr0()
                components.append(self.ast('FieldDefn', [texpr], value=name))
                self.consume(';')
            self.expect("}")
            scope_children = []
            if self.consume("for"):
                self.expect("(")
                idents = []
                if not self.on(")"):
                    idents.append(self.ast('Ident', value=self.expect_type('identifier')))
                    while self.consume(","):
                        idents.append(self.ast('Ident', value=self.expect_type('identifier')))
                self.expect(")")
                scope_children.append(self.ast('Idents', idents))
            return self.ast('StructDefn', [self.ast('FieldDefns', components)] + scope_children, value=id)
        else:
            id = self.expect_type('identifier')
            if self.consume('='):
                e = self.literal()
                return self.ast('Defn', [e], value=id)
            else:
                self.expect(':')
                e = self.texpr0()
                return self.ast('Forward', [e], value=id)

    def arg(self):
        id = self.expect_type('identifier')
        te = self.ast('Type', value='integer')
        if self.consume(':'):
            te = self.texpr1()
        return self.ast('Arg', [te], value=id)

    def texpr0(self):
        ast = self.texpr1()
        if self.consume('->'):
            r = self.texpr1()
            return self.ast('FunType', [r, ast])
        if self.on(','):
            args = [ast]
            while self.consume(','):
                args.append(self.texpr1())
            self.expect('->')
            r = self.texpr1()
            return self.ast('FunType', [r] + args)
        return ast

    def texpr1(self):
        ast = self.texpr2()
        if self.on('|'):
            args = [ast]
            while self.consume('|'):
                args.append(self.texpr2())
            ast = self.ast('UnionType', args)
        return ast

    def texpr2(self):
        if self.consume('('):
            ast = self.texpr0()
            self.expect(')')
            return ast
        elif self.on_type('identifier'):
            id = self.consume_type('identifier')
            return self.ast('StructType', [], value=id)
        tname = self.expect_type('type name')
        return self.ast('Type', value=tname)

    def block(self):
        self.expect('{')
        stmts = []
        while not self.on('}'):
            stmts.append(self.stmt())
            self.consume(';')
        self.expect('}')
        return self.ast('Block', stmts)

    STMT_TAGS = ('If', 'While', 'TypeCase', 'Return', 'Break')

    def body(self):
        # block for a function body -- automatically promotes the
        # last expression to a 'return' if it's not a statement
        # (and inserts a 'return' if the block is empty)
        self.expect('{')
        save_locals = self.locals
        self.locals = set()
        stmts = []
        last = None
        while not self.on('}'):
            last = self.stmt()
            stmts.append(last)
            self.consume(';')
        if len(stmts) == 0:
            stmts = [self.ast('Return', [self.ast('None')])]
        elif last is not None and last.tag not in self.STMT_TAGS:
            stmts[-1] = self.ast('Return', [stmts[-1]])
        self.expect('}')
        vardecls = self.ast(
            'VarDecls',
            [self.ast('VarDecl', value=name) for name in self.locals]
        )
        stmts = self.ast('Block', stmts)
        self.locals = save_locals
        return self.ast('Body', [vardecls, stmts])

    def stmt(self):
        if self.on('if'):
            return self.ifstmt()
        elif self.consume('while'):
            t = self.expr0()
            b = self.block()
            return self.ast('While', [t, b])
        elif self.consume('typecase'):
            id = self.expect_type('identifier')
            e = self.ast('VarRef', value=id)
            self.expect('is')
            te = self.texpr0()
            b = self.block()
            return self.ast('TypeCase', [e, te, b], value=te.minirepr())
        elif self.consume('return'):
            return self.ast('Return', [self.expr0()])
        elif self.consume('break'):
            return self.ast('Break')
        else:
            return self.expr0()

    def ifstmt(self):
        self.expect('if')
        t = self.expr0()
        b1 = self.block()
        if self.consume('else'):
            b2 = None
            if self.on('if'):
                b2 = self.ifstmt()
            else:
                b2 = self.block()
            return self.ast('If', [t, b1, b2])
        return self.ast('If', [t, b1])

    def expr0(self):
        e = self.expr1()
        while self.on_type('boolean operator'):
            op = self.expect_type('boolean operator')
            e2 = self.expr1()
            e = self.ast('Op', [e, e2], value=op)
        if self.consume('as'):
            union_te = self.texpr0()
            e = self.ast('TypeCast', [e, union_te])
        return e

    def expr1(self):
        e = self.expr2()
        while self.on_type('relational operator'):
            op = self.expect_type('relational operator')
            e2 = self.expr2()
            e = self.ast('Op', [e, e2], value=op)
        return e

    def expr2(self):
        e = self.expr3()
        while self.on_type('additive operator'):
            op = self.expect_type('additive operator')
            e2 = self.expr3()
            e = self.ast('Op', [e, e2], value=op)
        return e

    def expr3(self):
        e = self.expr4()
        while self.on_type('multiplicative operator'):
            op = self.expect_type('multiplicative operator')
            e2 = self.expr4()
            e = self.ast('Op', [e, e2], value=op)
        return e

    def expr4(self):
        e = self.expr5()
        done = False
        while not done:
            if self.consume('('):
                args = []
                if not self.on(")"):
                    args.append(self.expr0())
                    while self.consume(","):
                        args.append(self.expr0())
                self.expect(")")
                e = self.ast('FunCall', [e] + args)
            elif self.consume('.'):
                id = self.expect_type('identifier')
                e = self.ast('Index', [e], value=id)
            else:
                done = True
        return e

    def expr5(self):
        if self.on_type('string literal') or self.on_type('integer literal'):
            return self.literal()
        elif self.on_any(('-', 'fun', 'true', 'false', 'null')):
            return self.literal()
        elif self.consume('not'):
            return self.ast('Not', [self.expr1()])
        elif self.consume('make'):
            # TODO I just accidentally any type.  Is that bad?
            texpr = self.texpr0()
            self.expect('(')
            args = []
            if not self.on(')'):
                id = self.expect_type('identifier')
                self.expect(':')
                e = self.expr0()
                args.append(self.ast('FieldInit', [e], value=id))
                while self.consume(","):
                    id = self.expect_type('identifier')
                    self.expect(':')
                    e = self.expr0()
                    args.append(self.ast('FieldInit', [e], value=id))
            self.expect(")")
            return self.ast('Make', [texpr] + args, value=texpr.minirepr())

        elif self.consume('('):
            e = self.expr0()
            self.expect(')')
            return e
        else:
            id = self.expect_type('identifier')
            ast = self.ast('VarRef', value=id)
            if self.consume('='):
                e = self.expr0()
                aux = None
                if id not in self.locals:
                    self.locals.add(id)
                    aux = 'defining instance'
                ast = self.ast('Assignment', [ast, e], aux=aux)
            return ast

    def literal(self):
        if self.on_type('string literal'):
            v = self.consume_type('string literal')
            return self.ast('StrLit', value=v)
        elif self.on_type('integer literal'):
            v = int(self.consume_type('integer literal'))
            return self.ast('IntLit', value=v)
        elif self.consume('-'):
            v = 0 - int(self.expect_type('integer literal'))
            return self.ast('IntLit', value=v)
        elif self.consume('true'):
            return self.ast('BoolLit', value=True)
        elif self.consume('false'):
            return self.ast('BoolLit', value=False)
        elif self.consume('null'):
            return self.ast('None')
        else:
            self.expect('fun')
            self.expect("(")
            args = []
            if not self.on(")"):
                args.append(self.arg())
                while self.consume(","):
                    args.append(self.arg())
            self.expect(")")
            body = self.body()
            return self.ast('FunLit', [self.ast('Args', args), body])
