class CastileContextError(ValueError):
    pass


class ScopedContext(object):
    def __init__(self, dict, parent=None, level=None):
        self._dict = dict
        self.parent = parent
        self._level = level

    def level(self, key):
        if key in self._dict:
            return self._level
        return self.parent.level(key)

    def __getitem__(self, key):
        if key in self._dict:
            return self._dict[key]
        if self.parent is None:
            raise CastileContextError('undefined identifier %s' % key)
        return self.parent[key]

    def __setitem__(self, key, value):
        if key in self._dict:
            raise CastileContextError('duplicate defined identifier %s' % key)
        self._dict[key] = value

    def __contains__(self, key):
        if key in self._dict:
            return True
        if self.parent is None:
            return False
        return key in self.parent

    def __repr__(self):
        return 'ScopedContext(%r,parent=%r)' % (self._dict, self.parent)
