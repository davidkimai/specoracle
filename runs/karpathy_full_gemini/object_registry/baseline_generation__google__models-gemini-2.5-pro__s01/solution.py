import weakref
from typing import TypeVar, Generic, Hashable, Optional, Dict

# Define generic type variables for keys and values.
# K must be hashable to be used as a dictionary key.
K = TypeVar('K', bound=Hashable)
V = TypeVar('V')


class ObjectRegistry(Generic[K, V]):
    """
    A registry for objects that stores them as weak references.

    This allows objects to be garbage-collected if no other strong references
    to them exist. The registry provides a way to look up objects by a key,
    but it will not keep them alive.
    """

    def __init__(self) -> None:
        """Initializes an empty object registry."""
        self._data: Dict[K, weakref.ref[V]] = {}

    def register(self, key: K, obj: V) -> None:
        """
        Registers an object with a given key using a weak reference.

        If a registration for the given key already exists, it will be
        overwritten.

        Args:
            key: The unique, hashable key to associate with the object.
            obj: The object to register.
        """
        self._data[key] = weakref.ref(obj)

    def get(self, key: K) -> Optional[V]:
        """
        Retrieves an object from the registry by its key.

        Args:
            key: The key of the object to retrieve.

        Returns:
            The object if it is still alive, or None if the key does not
            exist or the object has been garbage-collected.
        """
        weak_ref = self._data.get(key)
        if weak_ref:
            return weak_ref()
        return None

    def cleanup(self) -> None:
        """
        Removes all entries where the weakly-referenced object has been
        garbage-collected.

        This method iterates through the registry and purges any keys whose
        associated objects no longer exist. It can be called periodically to
        free up memory used by the registry itself.
        """
        self._data = {
            key: ref for key, ref in self._data.items() if ref() is not None
        }
