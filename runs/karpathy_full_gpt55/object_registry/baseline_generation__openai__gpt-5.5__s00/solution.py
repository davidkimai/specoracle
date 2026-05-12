import weakref
from collections.abc import Hashable
from typing import Any, Dict, Optional


class ObjectRegistry:
    """A small key-to-object registry backed by weak references."""

    def __init__(self) -> None:
        self._refs: Dict[Hashable, weakref.ReferenceType[Any]] = {}

    def register(self, key: Hashable, obj: Any) -> None:
        """
        Register an object under key.

        The object must support weak references. Python will raise TypeError for
        objects that cannot be weakly referenced, such as most built-in scalar
        types.
        """
        self._refs[key] = weakref.ref(obj)

    def get(self, key: Hashable) -> Optional[Any]:
        """
        Return the registered object for key, or None if absent or collected.
        """
        ref = self._refs.get(key)
        if ref is None:
            return None

        obj = ref()
        if obj is None:
            self._refs.pop(key, None)
        return obj

    def cleanup(self) -> None:
        """Remove entries whose referenced objects have been garbage-collected."""
        dead_keys = [key for key, ref in self._refs.items() if ref() is None]
        for key in dead_keys:
            self._refs.pop(key, None)
