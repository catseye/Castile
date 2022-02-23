import re


class CastileSyntaxError(ValueError):
    pass


class Scanner(object):

    def __init__(self, text):
        self.text = text
        self.token = None
        self.type = None
        self.pos = 0
        self.line = 1
        self.scan()

    def near_text(self, length=10):
        return self.text[self.pos:self.pos + length]

    def scan_pattern(self, pattern, type, token_group=1, rest_group=2):
        pattern = r'(' + pattern + r')'
        regexp = re.compile(pattern, flags=re.DOTALL)
        match = regexp.match(self.text, pos=self.pos)
        if not match:
            return False
        else:
            self.type = type
            self.token = match.group(token_group)
            self.pos += len(match.group(0))
            self.line += self.token.count('\n')
            return True

    def scan(self):
        self.scan_pattern(r'[ \t\n\r]*', 'whitespace')
        while self.scan_pattern(r'\/\*.*?\*\/[ \t\n\r]*', 'comment'):
            self.scan_pattern(r'[ \t\n\r]*', 'whitespace')
        if self.pos >= len(self.text):
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
        if self.scan_pattern(r'(if|else|while|make|struct|'
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
            raise CastileSyntaxError(
                "Expected '%s', but found '%s' (line %s, near '%s')" % (
                    token, self.token, self.line, self.near_text()
                )
            )

    def expect_type(self, type):
        self.check_type(type)
        token = self.token
        self.scan()
        return token

    def on(self, token):
        return self.token == token

    def on_any(self, tokens):
        return self.token in tokens

    def on_type(self, type):
        return self.type == type

    def check_type(self, type):
        if not self.type == type:
            raise CastileSyntaxError(
                "Expected %s, but found %s ('%s') (line %s, near '%s')" % (
                    type, self.type, self.token, self.line, self.near_text()
                )
            )

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
