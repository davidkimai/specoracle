"""
A module for a weak-referencing object registry.

This module provides an ObjectRegistry class that stores objects using
weak references, allowing them to be garbage-collected when no longer
in use elsewhere.
"""

import weakref
from typing import Any, Dict, Hashable, Optional, TypeVar

T = TypeVar('T')


class ObjectRegistry:
    """
    A registry for objects that holds weak references to them.

    This allows registered objects to be garbage-collected if they are no
    longer strongly referenced elsewhere, preventing memory leaks that
    can be caused by a registry holding strong references.
    """

    def __init__(self) -> None:
        """Initializes an empty object registry."""
        self._registry: Dict[Hashable, weakref.ref[Any]] = {}

    def register(self, key: Hashable, obj: T) -> None:
        """
        Registers an object with a given key using a weak reference.

        Args:
            key: A hashable key to identify the object.
            obj: The object to register. It must be weak-referenceable.

        Raises:
            TypeError: If the key is not hashable or the object is not
                       weak-referenceable.
        """
        if not isinstance(key, Hashable):
            raise TypeError("Registry keys must be hashable.")

        # weakref.ref will raise TypeError if obj is not weak-referenceable.
        # This is the desired behavior, so we let it propagate to the caller.
        self._registry[key] = weakref.ref(obj)

    def get(self, key: Hashable) -> Optional[T]:
        """
        Retrieves an object by its key.

        If the object has been garbage-collected, this method returns None.

        Args:
            key: The key of the object to retrieve.

        Returns:
            The object if it is still alive, otherwise None.
            Also returns None if the key is not found in the registry.
        """
        weak_ref = self._registry.get(key)
        if weak_ref is None:
            return None

        # Dereference the weak reference. This returns the object
        # or None if it has been garbage-collected.
        return weak_ref()

    def cleanup(self) -> None:
        """
        Removes all entries for objects that have been garbage-collected.

        This method should be called periodically to free up space in the
        registry taken by keys whose corresponding objects have expired.
        """
        dead_keys = [
            key for key, weak_ref in self._registry.items()
            if weak_ref() is None
        ]

        for key in dead_keys:
            del self._registry[key]
