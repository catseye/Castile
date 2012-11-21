class AST(object):
    def __init__(self, type, children=None, value=None):
        # TODO 'type' should be 'tag' or 'kind' or smth; 'type' should be
        # the type, in the type system, of the value this node evaluates to
        self._type = type
        self._value = value
        if children is not None:
            self._children = children
        else:
            self._children = []
        assert isinstance(self.children, list)
        for child in self.children:
            assert isinstance(child, AST), \
              "child %r of %r is not an AST node" % (child, self)
        #print "created %r" % self

    @property
    def type(self):
        return self._type

    @property
    def value(self):
        return self._value

    @property
    def children(self):
        return self._children

    def __repr__(self):
        if self.value is None:
            return 'AST(%r,%r)' % (self.type, self.children)
        if not self.children:
            return 'AST(%r,value=%r)' % (self.type, self.value)
        return 'AST(%r,%r,value=%r)' % (self.type, self.children, self.value)

    def minirepr(self):
        return '%s(%s:%s)' % (
            self.type, self.value,
            ','.join([c.minirepr() for c in self.children])
        )

    def pprint(self, indent):
        h = ('  ' * indent) + self.type
        if self.value is not None:
            h += '=%r' % self.value
        h += '\n'
        for child in self.children:
            h += child.pprint(indent + 1)
        return h
