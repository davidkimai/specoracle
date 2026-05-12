# object_registry.py

"""
A module providing an object registry that uses weak references to prevent
memory leaks.
"""

import weakref
from typing import Any, Dict, Hashable, Optional


class ObjectRegistry:
    """
    A registry for objects that uses weak references.

    This allows objects to be garbage-collected if they are no longer
    strongly referenced elsewhere, preventing the registry itself from
    causing memory leaks.
    """

    def __init__(self) -> None:
        """Initializes an empty ObjectRegistry."""
        self._registry: Dict[Hashable, weakref.ReferenceType] = {}

    def register(self, key: Hashable, obj: Any) -> None:
        """
        Registers an object with a given key using a weak reference.

        If a key is already present, its associated object reference will be
        overwritten.

        Args:
            key: A hashable key to identify the object.
            obj: The object to register. The object must be weak-referenceable.

        Raises:
            TypeError: If the object is not weak-referenceable (e.g., built-in
                       lists or dicts).
        """
        if not isinstance(key, Hashable):
            raise TypeError("Registry key must be hashable.")
        self._registry[key] = weakref.ref(obj)

    def get(self, key: Hashable) -> Optional[Any]:
        """
        Retrieves an object by its key.

        Args:
            key: The key of the object to retrieve.

        Returns:
            The object if it's still alive, otherwise None.
            Also returns None if the key is not found in the registry.
        """
        weak_ref = self._registry.get(key)
        if weak_ref:
            return weak_ref()  # Dereference: returns object or None
        return None

    def cleanup(self) -> None:
        """
        Removes all dead references from the registry.

        A dead reference is one whose referenced object has been
        garbage-collected. This method iterates through the registry and
        discards any entries for which the weak reference is no longer valid.
        """
        live_keys = [k for k, v in self._registry.items() if v() is not None]
        self._registry = {k: self._registry[k] for k in live_keys}
