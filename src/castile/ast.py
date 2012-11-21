class AST(object):
    def __init__(self, type, children=None, value=None):
        self.type = type  # TODO should be 'tag' or 'kind' or smth
        self.t = None  # TODO should be 'type'.  argh.
        self.value = value
        if children is not None:
            self.children = children
        else:
            self.children = []
        assert isinstance(self.children, list)
        for child in self.children:
            assert isinstance(child, AST), \
              "child %r of %r is not an AST node" % (child, self)
        #print "created %r" % self

    def __repr__(self):
        if self.value is None:
            return 'AST(%r,%r)' % (self.type, self.children)
        if not self.children:
            return 'AST(%r,value=%r)' % (self.type, self.value)
        return 'AST(%r,%r,value=%r)' % (self.type, self.children, self.value)

    def pprint(self, indent):
        h = ('  ' * indent) + self.type
        if self.value is not None:
            h += '=%r' % self.value
        h += '\n'
        for child in self.children:
            h += child.pprint(indent + 1)
        return h
