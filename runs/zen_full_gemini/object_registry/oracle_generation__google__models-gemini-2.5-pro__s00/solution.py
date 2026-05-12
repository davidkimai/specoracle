# -*- coding: utf-8 -*-
"""
A module for a weak-referencing object registry.

This module provides an ObjectRegistry class that stores objects using weak
references, allowing them to be garbage-collected when no other strong
references exist.
"""

import weakref


class ObjectRegistry:
    """
    A registry for objects that uses weak references to avoid memory leaks.

    This registry maps keys to objects. The references to the objects are
    weak, meaning the registry does not prevent an object from being
    garbage-collected.
    """

    def __init__(self):
        """Initializes an empty object registry."""
        self._registry = {}

    def register(self, key, obj):
        """
        Registers an object with a given key using a weak reference.

        If a key is already present, its value will be overwritten.

        Args:
            key: A hashable key for the object.
            obj: The object to register. The object must be weakly referenceable.

        Raises:
            TypeError: If the object is not weakly referenceable (e.g., lists
                       or dicts).
        """
        self._registry[key] = weakref.ref(obj)

    def get(self, key):
        """
        Retrieves an object by its key.

        Args:
            key: The key of the object to retrieve.

        Returns:
            The object if it is still alive and registered, otherwise None.
            None is returned if the key is not found or if the object it
            referenced has been garbage-collected.
        """
        weak_ref = self._registry.get(key)
        if weak_ref is None:
            return None
        return weak_ref()

    def cleanup(self):
        """
        Removes all entries for objects that have been garbage-collected.

        This method should be called periodically to free up memory used by
        the registry for dead references.
        """
        live_refs = {
            key: weak_ref
            for key, weak_ref in self._registry.items()
            if weak_ref() is not None
        }
        self._registry = live_refs
