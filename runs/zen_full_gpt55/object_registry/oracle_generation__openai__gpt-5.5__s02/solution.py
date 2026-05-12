import weakref
from typing import Any, Dict


class ObjectRegistry:
    """A registry that stores objects by key without keeping them alive."""

    def __init__(self) -> None:
        self._references: Dict[Any, weakref.ReferenceType] = {}

    def register(self, key: Any, obj: Any) -> None:
        """Store obj under key using a weak reference."""
        self._require_hashable_key(key)

        try:
            reference = weakref.ref(obj)
        except TypeError as exc:
            obj_type = type(obj).__name__
            raise TypeError(f"objects of type {obj_type!r} cannot be weakly referenced") from exc

        self._references[key] = reference

    def get(self, key: Any) -> Any:
        """Return the live object for key, or None if absent or garbage-collected."""
        self._require_hashable_key(key)

        reference = self._references.get(key)
        if reference is None:
            return None

        return reference()

    def cleanup(self) -> None:
        """Remove entries whose objects have been garbage-collected."""
        dead_keys = [
            key
            for key, reference in self._references.items()
            if reference() is None
        ]

        for key in dead_keys:
            del self._references[key]

    @staticmethod
    def _require_hashable_key(key: Any) -> None:
        try:
            hash(key)
        except TypeError as exc:
            raise TypeError("registry keys must be hashable") from exc
