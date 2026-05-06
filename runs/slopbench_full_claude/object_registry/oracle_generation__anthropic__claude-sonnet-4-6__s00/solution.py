import weakref


class ObjectRegistry:
    """Registry that holds weak references to objects."""

    def __init__(self):
        self._store: dict[object, weakref.ref] = {}

    def register(self, key, obj) -> None:
        """Store a weak reference to *obj* under *key*."""
        self._store[key] = weakref.ref(obj)

    def get(self, key):
        """Return the object for *key*, or None if absent or garbage-collected."""
        ref = self._store.get(key)
        if ref is None:
            return None
        return ref()

    def cleanup(self) -> None:
        """Remove entries whose referents have been garbage-collected."""
        dead_keys = [key for key, ref in self._store.items() if ref() is None]
        for key in dead_keys:
            del self._store[key]
