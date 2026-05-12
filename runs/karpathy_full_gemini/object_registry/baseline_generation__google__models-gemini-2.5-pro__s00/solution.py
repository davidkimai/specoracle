import weakref
from typing import Any, Dict, Hashable, Optional


class ObjectRegistry:
    """
    A registry for objects that uses weak references to avoid preventing
    garbage collection.

    This allows for associating objects with keys without creating strong
    references that would keep them in memory indefinitely.
    """

    def __init__(self) -> None:
        """Initializes an empty object registry."""
        self._registry: Dict[Hashable, weakref.ref[Any]] = {}

    def register(self, key: Hashable, obj: Any) -> None:
        """
        Registers an object with a given key using a weak reference.

        If the object is not weakly referenceable (e.g., built-in types like
        list or dict), a `TypeError` will be raised by `weakref.ref`.

        Args:
            key: The hashable key to associate with the object.
            obj: The object to register.
        """
        if not isinstance(key, Hashable):
            raise TypeError("Registry keys must be hashable.")
        self._registry[key] = weakref.ref(obj)

    def get(self, key: Hashable) -> Optional[Any]:
        """
        Retrieves an object by its key.

        Returns the object if it's still alive, otherwise returns None.
        This also returns None if the key is not found in the registry.

        Args:
            key: The key of the object to retrieve.

        Returns:
            The object associated with the key, or None if the key is not
            found or the object has been garbage-collected.
        """
        weak_ref = self._registry.get(key)
        if weak_ref:
            # Dereference the weak reference. It will be None if the object
            # has been garbage-collected.
            return weak_ref()
        return None

    def cleanup(self) -> None:
        """
        Removes entries for objects that have been garbage-collected.

        This method iterates through the registry and discards any keys
        whose corresponding weak reference is no longer valid.
        """
        self._registry = {
            key: weak_ref
            for key, weak_ref in self._registry.items()
            if weak_ref() is not None
        }
