class AST(object):
    def __init__(self, tag, children=None, value=None, type=None, aux=None):
        self.tag = tag
        self.value = value
        # typechecker may populate this.  parser will not.
        self.type = type
        # typechecker may populate this.  parser will not.
        # on VarRef nodes, this is the level of the reference
        #  ('global', 'toplevel', 'argument', 'local', or 'typecase')
        # on FieldInit and Index nodes, this is the position
        #  (offset) of the field within the struct
        self.aux = aux
        if children is not None:
            self.children = children
        else:
            self.children = []
        assert isinstance(self.children, list)
        for child in self.children:
            assert isinstance(child, AST), \
              "child %r of %r is not an AST node" % (child, self)
        #print "created %r" % self

    def copy(self, children=None, value=None, type=None, aux=None):
        if children is None:
            children = self.children
        if value is None:
            value = self.value
        if type is None:
            type = self.type
        if aux is None:
            aux = self.aux
        return AST(self.tag, children=children, value=value,
                   type=type, aux=aux)

    def __repr__(self):
        if self.value is None:
            return 'AST(%r,%r)' % (self.tag, self.children)
        if not self.children:
            return 'AST(%r,value=%r)' % (self.tag, self.value)
        return 'AST(%r,%r,value=%r)' % (self.tag, self.children, self.value)

    def minirepr(self):
        return '%s(%s:%s)' % (
            self.tag, self.value,
            ','.join([c.minirepr() for c in self.children])
        )

    def pprint(self, indent):
        h = ('  ' * indent) + self.tag
        if self.value is not None:
            h += '=%r' % self.value
        h += '\n'
        for child in self.children:
            h += child.pprint(indent + 1)
        return h
