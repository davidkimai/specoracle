import weakref
from typing import Any, Hashable, Optional


class ObjectRegistry:
    """A small registry that stores objects by key using weak references."""

    def __init__(self) -> None:
        self._references: dict[Hashable, weakref.ReferenceType[Any]] = {}

    def register(self, key: Hashable, obj: Any) -> None:
        """Store obj under key without keeping obj alive."""
        try:
            reference = weakref.ref(obj)
        except TypeError as error:
            raise TypeError(
                f"object of type {type(obj).__name__!r} cannot be weakly referenced"
            ) from error

        self._references[key] = reference

    def get(self, key: Hashable) -> Optional[Any]:
        """Return the live object for key, or None if missing or collected."""
        reference = self._references.get(key)
        if reference is None:
            return None
        return reference()

    def cleanup(self) -> None:
        """Remove entries whose objects have been garbage-collected."""
        dead_keys = [
            key for key, reference in self._references.items() if reference() is None
        ]

        for key in dead_keys:
            del self._references[key]
