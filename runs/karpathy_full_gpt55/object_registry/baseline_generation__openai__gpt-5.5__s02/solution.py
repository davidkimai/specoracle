import weakref
from typing import Any, Dict, Hashable, Optional


class ObjectRegistry:
    """A registry that stores objects by key using weak references."""

    def __init__(self) -> None:
        self._refs: Dict[Hashable, weakref.ReferenceType[Any]] = {}

    def register(self, key: Hashable, obj: Any) -> None:
        """
        Store an object under the given key using a weak reference.

        Raises:
            TypeError: If the object does not support weak references.
        """
        self._refs[key] = weakref.ref(obj)

    def get(self, key: Hashable) -> Optional[Any]:
        """
        Return the object registered for key, or None if missing or collected.
        """
        ref = self._refs.get(key)
        if ref is None:
            return None
        return ref()

    def cleanup(self) -> None:
        """Remove entries whose referenced objects have been garbage-collected."""
        dead_keys = [key for key, ref in self._refs.items() if ref() is None]
        for key in dead_keys:
            self._refs.pop(key, None)
