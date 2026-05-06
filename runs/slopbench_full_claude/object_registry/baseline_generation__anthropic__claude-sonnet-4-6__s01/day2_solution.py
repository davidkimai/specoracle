import weakref


class ObjectRegistry:
    def __init__(self):
        self._store = {}
        self._tags = {}  # tag -> set of keys

    def register(self, key, obj, tags=None):
        self._store[key] = weakref.ref(obj)
        if tags:
            for tag in tags:
                self._tags.setdefault(tag, set()).add(key)

    def get(self, key):
        ref = self._store.get(key)
        if ref is None:
            return None
        return ref()

    def by_tag(self, tag):
        keys = self._tags.get(tag, set())
        result = []
        for key in keys:
            ref = self._store.get(key)
            if ref is not None:
                obj = ref()
                if obj is not None:
                    result.append(obj)
        return result

    def cleanup(self):
        dead_keys = [key for key, ref in self._store.items() if ref() is None]
        for key in dead_keys:
            del self._store[key]
        for tag, keys in self._tags.items():
            keys.difference_update(dead_keys)
