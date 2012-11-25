import re

from castile.ast import AST


class CastileSyntaxError(ValueError):
    pass


class Parser(object):
    """Parse a Castile program into an AST.

    The parser includes the scanner as part of it.  (Delegating to an external
    scanner is rather verbose ("self.scanner.expect(...)"; inheriting from a
    Scanner class, even if it's just a mixin, seems rather weird.)

    The parser mainly just constructs the AST.  It does few other analyses
    or transformations itself.  However, there are a few:

    * It inserts a final `return` in a block where the last statement is a
      non-void expression.

    """
    def __init__(self, text):
        self.text = text
        self.token = None
        self.type = None
        self.scan()

    ### SCANNER ###

    def scan_pattern(self, pattern, type, token_group=1, rest_group=2):
        pattern = r'^(' + pattern + r')(.*?)$'
        match = re.match(pattern, self.text, re.DOTALL)
        if not match:
            return False
        else:
            self.type = type
            self.token = match.group(token_group)
            self.text = match.group(rest_group)
            #print self.type, self.token
            return True

    def scan(self):
        self.scan_pattern(r'[ \t\n\r]*', 'whitespace')
        while self.text.startswith('/*'):
            self.scan_pattern(r'\/\*.*?\*\/[ \t\n\r]*', 'comment')
        if not self.text:
            self.token = None
            self.type = 'EOF'
            return
        if self.scan_pattern(r'->', 'arrow'):
            return
        if self.scan_pattern(r'>=|>|<=|<|==|!=', 'relational operator'):
            return
        if self.scan_pattern(r'\+|\-', 'additive operator'):
            return
        if self.scan_pattern(r'\*|\/|\|', 'multiplicative operator'):
            return
        if self.scan_pattern(r'\.|\;|\,|\(|\)|\{|\}|\=', 'punctuation'):
            return
        if self.scan_pattern(r'string|integer|boolean|function|void|union',
                             'type name'):
            return
        if self.scan_pattern(r'and|or', 'boolean operator'):
            return
        if self.scan_pattern(r'(var|if|else|while|make|struct|'
                             r'typecase|is|as|return|break|'
                             r'true|false|null)(?!\w)',
                             'keyword', token_group=2, rest_group=3):
            return
        if self.scan_pattern(r'\d+', 'integer literal'):
            return
        if self.scan_pattern(r'\"(.*?)\"', 'string literal',
                             token_group=2, rest_group=3):
            return
        if self.scan_pattern(r'[a-zA-Z_][a-zA-Z0-9_]*', 'identifier'):
            return
        if self.scan_pattern(r'.', 'unknown character'):
            return
        else:
            raise ValueError("this should never happen, "
                             "self.text=(%s)" % self.text)

    def expect(self, token):
        if self.token == token:
            self.scan()
        else:
            raise CastileSyntaxError("Expected '%s', but found '%s'" %
                              (token, self.token))

    def expect_type(self, type):
        self.check_type(type)
        token = self.token
        self.scan()
        return token

    def on(self, token):
        return self.token == token

    def on_type(self, type):
        return self.type == type

    def check_type(self, type):
        if not self.type == type:
            raise CastileSyntaxError("Expected %s, but found %s ('%s')" %
                              (type, self.type, self.token))

    def consume(self, token):
        if self.token == token:
            self.scan()
            return True
        else:
            return False

    def consume_type(self, type):
        if self.on_type(type):
            token = self.token
            self.scan()
            return token
        else:
            return None

    ### PARSER ###

    def program(self):
        defns = []
        while not self.on_type('EOF'):
            defns.append(self.defn())
            self.consume(';')
        return AST('Program', defns)

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
            funlit = AST('FunLit', [AST('Args', args), body])
            return AST('Defn', [funlit], value=id)
        elif self.consume('struct'):
            id = self.expect_type('identifier')
            self.expect("{")
            components = []
            while not self.on('}'):
                name = self.expect_type('identifier')
                self.expect(':')
                texpr = self.texpr0()
                components.append(AST('FieldDefn', [texpr], value=name))
                self.consume(';')
            self.expect("}")
            return AST('StructDefn', components, value=id)
        else:
            id = self.expect_type('identifier')
            if self.consume('='):
                e = self.literal()
                return AST('Defn', [e], value=id)
            else:
                self.expect(':')
                e = self.texpr0()
                return AST('Forward', [e], value=id)

    def arg(self):
        id = self.expect_type('identifier')
        te = AST('Type', value='integer')
        if self.consume(':'):
            te = self.texpr1()
        return AST('Arg', [te], value=id)

    def texpr0(self):
        ast = self.texpr1()
        if self.consume('->'):
            r = self.texpr1()
            return AST('FunType', [r, ast])
        if self.on(','):
            args = [ast]
            while self.consume(','):
                args.append(self.texpr1())
            self.expect('->')
            r = self.texpr1()
            return AST('FunType', [r] + args)
        return ast

    def texpr1(self):
        ast = self.texpr2()
        if self.on('|'):
            args = [ast]
            while self.consume('|'):
                args.append(self.texpr2())
            ast = AST('UnionType', args)
        return ast

    def texpr2(self):
        if self.consume('('):
            ast = self.texpr0()
            self.expect(')')
            return ast
        elif self.on_type('identifier'):
            id = self.consume_type('identifier')
            return AST('StructType', [], value=id)
        tname = self.expect_type('type name')
        return AST('Type', value=tname)

    def block(self):
        self.expect('{')
        stmts = []
        while not self.on('}'):
            stmts.append(self.stmt())
            self.consume(';')
        self.expect('}')
        return AST('Block', stmts)

    STMT_TAGS = ('If', 'While', 'TypeCase', 'Return', 'Break')

    def body(self):
        # block for a function body -- automatically promotes the
        # last expression to a 'return' if it's not a statement
        # (and inserts a 'return' if the block is empty)
        self.expect('{')
        vardecls = []
        while self.consume('var'):
            id = self.expect_type('identifier')
            self.expect('=')
            e = self.expr0()
            vardecls.append(AST('VarDecl', [e], value=id))
            self.consume(';')
        stmts = []
        last = None
        while not self.on('}'):
            last = self.stmt()
            stmts.append(last)
            self.consume(';')
        if len(stmts) == 0:
            stmts = [AST('Return', [AST('None')])]
        elif last is not None and last.tag not in self.STMT_TAGS:
            stmts[-1] = AST('Return', [stmts[-1]])
        self.expect('}')
        vardecls = AST('VarDecls', vardecls)
        stmts = AST('Block', stmts)
        return AST('Body', [vardecls, stmts])

    def stmt(self):
        if self.on('if'):
            return self.ifstmt()
        elif self.consume('while'):
            t = self.expr0()
            b = self.block()
            return AST('While', [t, b])
        elif self.consume('typecase'):
            id = self.expect_type('identifier')
            e = AST('VarRef', value=id)
            self.expect('is')
            te = self.texpr0()
            b = self.block()
            return AST('TypeCase', [e, te, b], value=te.minirepr())
        elif self.consume('return'):
            return AST('Return', [self.expr0()])
        elif self.consume('break'):
            return AST('Break')
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
            return AST('If', [t, b1, b2])
        return AST('If', [t, b1])

    def expr0(self):
        e = self.expr1()
        while self.on_type('boolean operator'):
            op = self.expect_type('boolean operator')
            e2 = self.expr1()
            e = AST('Op', [e, e2], value=op)
        if self.consume('as'):
            union_te = self.texpr0()
            e = AST('TypeCast', [e, union_te])
        return e

    def expr1(self):
        e = self.expr2()
        while self.on_type('relational operator'):
            op = self.expect_type('relational operator')
            e2 = self.expr2()
            e = AST('Op', [e, e2], value=op)
        return e

    def expr2(self):
        e = self.expr3()
        while self.on_type('additive operator'):
            op = self.expect_type('additive operator')
            e2 = self.expr3()
            e = AST('Op', [e, e2], value=op)
        return e

    def expr3(self):
        e = self.expr4()
        while self.on_type('multiplicative operator'):
            op = self.expect_type('multiplicative operator')
            e2 = self.expr4()
            e = AST('Op', [e, e2], value=op)
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
                e = AST('FunCall', [e] + args)
            elif self.consume('.'):
                id = self.expect_type('identifier')
                e = AST('Index', [e], value=id)
            else:
                done = True
        return e

    def expr5(self):
        if (self.on_type('string literal') or self.on('-') or
            self.on_type('integer literal') or self.on('fun')
            or self.on('true') or self.on('false') or self.on('null')):
            return self.literal()
        elif self.consume('not'):
            return AST('Not', [self.expr1()])
        elif self.consume('make'):
            # TODO I just accidentally any type.  Is that bad?
            texpr = self.texpr0()
            self.expect('(')
            args = []
            if not self.on(')'):
                id = self.expect_type('identifier')
                self.expect(':')
                e = self.expr0()
                args.append(AST('FieldInit', [e], value=id))
                while self.consume(","):
                    id = self.expect_type('identifier')
                    self.expect(':')
                    e = self.expr0()
                    args.append(AST('FieldInit', [e], value=id))
            self.expect(")")
            return AST('Make', [texpr] + args, value=texpr.minirepr())

        elif self.consume('('):
            e = self.expr0()
            self.expect(')')
            return e
        else:
            id = self.expect_type('identifier')
            ast = AST('VarRef', value=id)
            if self.consume('='):
                e = self.expr0()
                ast = AST('Assignment', [ast, e])
            return ast

    def literal(self):
        if self.on_type('string literal'):
            v = self.consume_type('string literal')
            return AST('StrLit', value=v)
        elif self.on_type('integer literal'):
            v = int(self.consume_type('integer literal'))
            return AST('IntLit', value=v)
        elif self.consume('-'):
            v = 0 - int(self.expect_type('integer literal'))
            return AST('IntLit', value=v)
        elif self.consume('true'):
            return AST('BoolLit', value=True)
        elif self.consume('false'):
            return AST('BoolLit', value=False)
        elif self.consume('null'):
            return AST('None')
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
            return AST('FunLit', [AST('Args', args), body])
