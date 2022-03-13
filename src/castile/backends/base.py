"""Abstract base class for Castile compiler backends,
especially source-to-source."""

class BaseCompiler(object):
    def __init__(self, out):
        self.out = out
        self.indent = 0

    def commas(self, asts, sep=','):
        if asts:
            for child in asts[:-1]:
                self.compile(child)
                self.out.write(sep)
            self.compile(asts[-1])

    def write(self, x):
        self.out.write(x)

    def write_indent(self, x):
        self.out.write('    ' * self.indent)
        self.out.write(x)
