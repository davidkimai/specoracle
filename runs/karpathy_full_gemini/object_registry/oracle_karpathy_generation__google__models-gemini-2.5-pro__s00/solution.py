import weakref
from typing import Any, Dict, Hashable, Optional


class ObjectRegistry:
    """
    A registry for objects that stores them as weak references.

    This allows objects to be garbage-collected when no other strong
    references to them exist, preventing memory leaks from the registry
    itself.
    """

    def __init__(self) -> None:
        """Initializes an empty ObjectRegistry."""
        self._registry: Dict[Hashable, weakref.ref[Any]] = {}

    def register(self, key: Hashable, obj: Any) -> None:
        """
        Registers an object with a given key using a weak reference.

        If a key is already present, its associated object reference
        will be overwritten.

        Args:
            key: The hashable key to associate with the object.
            obj: The object to register.
        """
        if not isinstance(key, Hashable):
            raise TypeError("Key must be hashable")
        self._registry[key] = weakref.ref(obj)

    def get(self, key: Hashable) -> Optional[Any]:
        """
        Retrieves an object by its key.

        Args:
            key: The key of the object to retrieve.

        Returns:
            The object if the key exists and the object has not been
            garbage-collected. Otherwise, returns None.
        """
        weak_ref = self._registry.get(key)
        if weak_ref is None:
            return None
        return weak_ref()

    def cleanup(self) -> None:
        """
        Removes all entries for objects that have been garbage-collected.

        This method should be called periodically to free up memory used
        by the registry for dead references.
        """
        dead_keys = [
            key for key, weak_ref in self._registry.items() if weak_ref() is None
        ]
        for key in dead_keys:
            del self._registry[key]
