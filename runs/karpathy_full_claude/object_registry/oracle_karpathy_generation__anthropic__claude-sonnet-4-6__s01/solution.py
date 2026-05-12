import weakref


class ObjectRegistry:
    def __init__(self):
        self._store = {}

    def register(self, key, obj):
        self._store[key] = weakref.ref(obj)

    def get(self, key):
        ref = self._store.get(key)
        if ref is None:
            return None
        return ref()

    def cleanup(self):
        dead = [k for k, ref in self._store.items() if ref() is None]
        for k in dead:
            del self._store[k]
