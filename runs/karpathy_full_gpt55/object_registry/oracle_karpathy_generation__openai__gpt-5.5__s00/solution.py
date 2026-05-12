import weakref


class ObjectRegistry:
    """Registry that stores weak references to registered objects.

    Registered objects must support weak references.
    """

    def __init__(self):
        self._refs = {}

    def register(self, key, obj):
        self._refs[key] = weakref.ref(obj)

    def get(self, key):
        ref = self._refs.get(key)
        if ref is None:
            return None
        return ref()

    def cleanup(self):
        dead_keys = [key for key, ref in self._refs.items() if ref() is None]
        for key in dead_keys:
            del self._refs[key]
