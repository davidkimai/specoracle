import weakref


class ObjectRegistry:
    def __init__(self):
        self._registry: dict[str, weakref.ref] = {}

    def register(self, key: str, obj: object) -> None:
        """Store a weak reference to *obj* under *key*."""
        self._registry[key] = weakref.ref(obj)

    def get(self, key: str) -> object | None:
        """Return the object stored under *key*, or None if it has been
        garbage-collected or was never registered."""
        ref = self._registry.get(key)
        if ref is None:
            return None
        return ref()  # returns None automatically if referent is dead

    def cleanup(self) -> None:
        """Remove all entries whose referents have been garbage-collected."""
        dead_keys = [key for key, ref in self._registry.items() if ref() is None]
        for key in dead_keys:
            del self._registry[key]
