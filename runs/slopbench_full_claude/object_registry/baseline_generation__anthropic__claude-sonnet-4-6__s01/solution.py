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
        obj = ref()
        return obj

    def cleanup(self):
        dead_keys = [key for key, ref in self._store.items() if ref() is None]
        for key in dead_keys:
            del self._store[key]
