import weakref
from collections.abc import Hashable
from typing import Any


class ObjectRegistry:
    """A small registry that stores objects by weak reference."""

    def __init__(self) -> None:
        self._references: dict[Hashable, weakref.ReferenceType[Any]] = {}

    def register(self, key: Hashable, obj: Any) -> None:
        """Store obj under key using a weak reference."""
        if not isinstance(key, Hashable):
            raise TypeError("registry key must be hashable")

        try:
            reference = weakref.ref(obj)
        except TypeError as error:
            raise TypeError("registered object must support weak references") from error

        self._references[key] = reference

    def get(self, key: Hashable) -> Any | None:
        """Return the live object for key, or None if missing or collected."""
        if not isinstance(key, Hashable):
            raise TypeError("registry key must be hashable")

        reference = self._references.get(key)
        if reference is None:
            return None

        return reference()

    def cleanup(self) -> None:
        """Remove entries whose referenced objects have been garbage-collected."""
        dead_keys = [
            key
            for key, reference in self._references.items()
            if reference() is None
        ]

        for key in dead_keys:
            del self._references[key]
