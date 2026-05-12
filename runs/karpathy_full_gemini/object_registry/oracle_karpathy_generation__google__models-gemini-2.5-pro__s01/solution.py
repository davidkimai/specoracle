import weakref
from typing import Any, Dict, Optional

class ObjectRegistry:
    """
    A registry for objects that holds weak references to them.

    This allows objects to be garbage-collected if no other strong references
    to them exist.
    """

    def __init__(self) -> None:
        """Initializes an empty object registry."""
        self._registry: Dict[Any, weakref.ref] = {}

    def register(self, key: Any, obj: object) -> None:
        """
        Registers an object with a given key using a weak reference.

        If a registration already exists for the given key, it is overwritten.

        Args:
            key: The key to associate with the object. Must be hashable.
            obj: The object to register.
        """
        self._registry[key] = weakref.ref(obj)

    def get(self, key: Any) -> Optional[object]:
        """
        Retrieves an object from the registry by its key.

        Returns the object if it is still alive, otherwise returns None.
        Also returns None if the key is not found in the registry.

        Args:
            key: The key of the object to retrieve.

        Returns:
            The registered object or None if it has been garbage-collected
            or the key does not exist.
        """
        weak_ref = self._registry.get(key)
        if weak_ref is None:
            return None
        
        return weak_ref()

    def cleanup(self) -> None:
        """
        Removes all dead references from the registry.

        A dead reference is one that points to an object that has been
        garbage-collected. This method should be called periodically to
        prevent the registry from growing with dead entries.
        """
        live_refs = {
            key: weak_ref
            for key, weak_ref in self._registry.items()
            if weak_ref() is not None
        }
        self._registry = live_refs
