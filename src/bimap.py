# bimap.py - small bidirectional map compatible with CPython and MicroPython

class BiMap:
    """
    Simple bidirectional mapping: keys <-> values.
    Keys and values must be hashable.
    By default put() will raise if key or value already exists mapping to a different counterpart.
    You can use overwrite=True to replace existing mappings.
    """

    def __init__(self, data=None, *, overwrite=False):
        # forward: key -> value
        # backward: value -> key
        self._fwd = {}
        self._bwd = {}
        self._overwrite = bool(overwrite)
        if data:
            for k, v in data:
                self.put(k, v, overwrite=self._overwrite)

    # core API
    def put(self, key, value, overwrite=None):
        """Insert key->value. If overwrite is False (default) and either key or value exists
           and maps to a different counterpart, raises ValueError.
           If overwrite True, previous mappings are removed/replaced.
        """
        if overwrite is None:
            overwrite = self._overwrite

        # check current mappings
        old_v = self._fwd.get(key, None)
        old_k = self._bwd.get(value, None)

        # if nothing to change, just assign
        if old_v is value and old_k is key:
            return

        # conflicts
        if not overwrite:
            if key in self._fwd and old_v is not value:
                raise ValueError("Key already mapped to different value")
            if value in self._bwd and old_k is not key:
                raise ValueError("Value already mapped to different key")

        # remove any existing mappings that conflict (if overwrite)
        if key in self._fwd and self._fwd[key] is not value:
            oldval = self._fwd.pop(key)
            try:
                del self._bwd[oldval]
            except KeyError:
                pass
        if value in self._bwd and self._bwd[value] is not key:
            oldkey = self._bwd.pop(value)
            try:
                del self._fwd[oldkey]
            except KeyError:
                pass

        # set new mapping
        self._fwd[key] = value
        self._bwd[value] = key

    def get(self, key, default=None):
        return self._fwd.get(key, default)

    def inverse_get(self, value, default=None):
        return self._bwd.get(value, default)

    def remove_by_key(self, key):
        """Remove mapping by key. Raises KeyError if key not present."""
        if key not in self._fwd:
            raise KeyError(key)
        val = self._fwd.pop(key)
        try:
            del self._bwd[val]
        except KeyError:
            pass

    def remove_by_value(self, value):
        """Remove mapping by value. Raises KeyError if value not present."""
        if value not in self._bwd:
            raise KeyError(value)
        key = self._bwd.pop(value)
        try:
            del self._fwd[key]
        except KeyError:
            pass

    def clear(self):
        self._fwd.clear()
        self._bwd.clear()

    # mapping protocol convenience
    def __setitem__(self, key, value):
        self.put(key, value)

    def __getitem__(self, key):
        return self._fwd[key]

    def __delitem__(self, key):
        self.remove_by_key(key)

    def __contains__(self, key):
        return key in self._fwd

    def __len__(self):
        return len(self._fwd)

    def keys(self):
        return list(self._fwd.keys())

    def values(self):
        return list(self._fwd.values())

    def items(self):
        return list(self._fwd.items())

    # inverse view (lightweight)
    @property
    def inverse(self):
        class _InvView(object):
            def __init__(self, bwd):
                self._bwd = bwd
            def __getitem__(self, v):
                return self._bwd[v]
            def get(self, v, default=None):
                return self._bwd.get(v, default)
            def __contains__(self, v):
                return v in self._bwd
            def keys(self):
                return list(self._bwd.keys())
            def values(self):
                return list(self._bwd.values())
            def items(self):
                return list(self._bwd.items())
        return _InvView(self._bwd)

    def __repr__(self):
        return "BiMap(" + repr(self._fwd) + ")"