"""A registry for objects that holds weak references."""

import weakref
from typing import Any, Dict, Hashable, Optional, TypeVar

T = TypeVar('T')


class ObjectRegistry:
    """
    A registry for objects that holds weak references to them.

    This allows registered objects to be garbage-collected when no other
    strong references to them exist, which helps prevent reference cycles
    and unnecessary memory consumption.
    """

    def __init__(self) -> None:
        """Initializes an empty object registry."""
        self._registry: Dict[Hashable, weakref.ReferenceType[Any]] = {}

    def register(self, key: Hashable, obj: T) -> None:
        """
        Registers an object with a given key using a weak reference.

        Args:
            key: A hashable key for the object.
            obj: The object to register. Must be weakly referenceable.

        Raises:
            TypeError: If the key is not hashable or the object is not
                       weakly referenceable (e.g., lists or dicts).
        """
        self._registry[key] = weakref.ref(obj)

    def get(self, key: Hashable) -> Optional[T]:
        """
        Retrieves an object by its key.

        Args:
            key: The key of the object to retrieve.

        Returns:
            The object if it's still alive, or None if the key does not
            exist or if the object has been garbage-collected.
        """
        weak_ref = self._registry.get(key)

        if weak_ref is None:
            return None

        # Dereferencing the weak reference returns the object or None if dead.
        return weak_ref()

    def cleanup(self) -> None:
        """
        Removes all entries for objects that have been garbage-collected.

        This method iterates through the registry and discards any keys
        that point to dead weak references.
        """
        live_refs = {
            key: weak_ref
            for key, weak_ref in self._registry.items()
            if weak_ref() is not None
        }
        self._registry = live_refs
