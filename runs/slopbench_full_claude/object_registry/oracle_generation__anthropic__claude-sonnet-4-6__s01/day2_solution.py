"""
object_registry.py

A registry that holds weak references to objects, allowing them to be
garbage-collected when no other strong references exist.
"""

import weakref


class ObjectRegistry:
    """Maps keys to weakly-referenced objects.

    - register(key, obj, tags): store a weak reference to obj under key,
      optionally associating it with a set of string tags.
    - get(key): return the live object, or None if collected or absent.
    - by_tag(tag): return a list of live objects registered with that tag.
    - cleanup(): remove entries whose referents have been garbage-collected.
    """

    def __init__(self):
        self._refs: dict[object, weakref.ref] = {}
        # Maps each tag to the set of keys registered under that tag.
        self._tag_index: dict[str, set] = {}

    def register(self, key, obj, tags: set[str] | None = None) -> None:
        """Store a weak reference to obj under key.

        Parameters
        ----------
        key:
            Hashable identifier for the object.
        obj:
            The object to register (must be weak-referenceable).
        tags:
            Optional set of string tags to associate with this entry.
        """
        self._refs[key] = weakref.ref(obj)

        # Update tag index: first remove key from any existing tags,
        # then add it to the new ones.
        for tag_keys in self._tag_index.values():
            tag_keys.discard(key)

        if tags:
            for tag in tags:
                self._tag_index.setdefault(tag, set()).add(key)

    def get(self, key):
        """Return the object for key, or None if absent or garbage-collected."""
        ref = self._refs.get(key)
        if ref is None:
            return None
        return ref()  # returns None if the referent has been collected

    def by_tag(self, tag: str) -> list:
        """Return a list of live objects registered with the given tag.

        Dead references are silently excluded.
        """
        keys = self._tag_index.get(tag, set())
        result = []
        for key in keys:
            obj = self.get(key)
            if obj is not None:
                result.append(obj)
        return result

    def cleanup(self) -> None:
        """Remove all entries whose referents have been garbage-collected."""
        dead_keys = [key for key, ref in self._refs.items() if ref() is None]
        for key in dead_keys:
            del self._refs[key]
            # Remove the dead key from all tag sets.
            for tag_keys in self._tag_index.values():
                tag_keys.discard(key)
        # Remove now-empty tag entries.
        empty_tags = [tag for tag, keys in self._tag_index.items() if not keys]
        for tag in empty_tags:
            del self._tag_index[tag]

    def __len__(self) -> int:
        return len(self._refs)

    def __contains__(self, key) -> bool:
        return self.get(key) is not None
