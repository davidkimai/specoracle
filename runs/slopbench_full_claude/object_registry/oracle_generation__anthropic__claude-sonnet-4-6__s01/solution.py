"""
object_registry.py

A registry that holds weak references to objects, allowing them to be
garbage-collected when no other strong references exist.
"""

import weakref


class ObjectRegistry:
    """Maps keys to weakly-referenced objects.

    - register(key, obj): store a weak reference to obj under key.
    - get(key): return the live object, or None if collected or absent.
    - cleanup(): remove entries whose referents have been garbage-collected.
    """

    def __init__(self):
        self._refs: dict[object, weakref.ref] = {}

    def register(self, key, obj) -> None:
        """Store a weak reference to obj under key."""
        self._refs[key] = weakref.ref(obj)

    def get(self, key):
        """Return the object for key, or None if absent or garbage-collected."""
        ref = self._refs.get(key)
        if ref is None:
            return None
        return ref()  # returns None if the referent has been collected

    def cleanup(self) -> None:
        """Remove all entries whose referents have been garbage-collected."""
        dead_keys = [key for key, ref in self._refs.items() if ref() is None]
        for key in dead_keys:
            del self._refs[key]

    def __len__(self) -> int:
        return len(self._refs)

    def __contains__(self, key) -> bool:
        return self.get(key) is not None
