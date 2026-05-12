import weakref
from typing import Any, Dict, Hashable, Optional, TypeVar

T = TypeVar('T')


class ObjectRegistry:
    """
    A registry for objects that uses weak references.

    This allows objects to be garbage-collected even if they are present
    in the registry, preventing reference cycles and memory leaks.
    """

    def __init__(self) -> None:
        """Initializes an empty ObjectRegistry."""
        self._registry: Dict[Hashable, weakref.ref[Any]] = {}

    def register(self, key: Hashable, obj: T) -> None:
        """
        Registers an object with a given key using a weak reference.

        Args:
            key: The hashable key to associate with the object.
            obj: The object to register. A weak reference to this object
                 will be stored. Note that not all objects are
                 weak-referenceable.
        """
        self._registry[key] = weakref.ref(obj)

    def get(self, key: Hashable) -> Optional[T]:
        """
        Retrieves an object by its key.

        Args:
            key: The key of the object to retrieve.

        Returns:
            The object if it's still alive and present in the registry.
            Returns None if the key is not found or if the object has been
            garbage-collected.
        """
        weak_ref = self._registry.get(key)
        if weak_ref is None:
            return None

        return weak_ref()

    def cleanup(self) -> None:
        """
        Removes all dead references from the registry.

        A reference is considered dead if the object it points to has been
        garbage-collected. This method can be called periodically to
        free up memory used by the registry for storing stale reference
        objects.
        """
        self._registry = {
            key: ref for key, ref in self._registry.items() if ref() is not None
        }
