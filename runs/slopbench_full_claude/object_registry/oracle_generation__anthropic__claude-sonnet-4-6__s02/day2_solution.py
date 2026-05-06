"""
object_registry.py

A registry that holds weak references to objects, allowing them to be
garbage-collected when no other references exist.
"""

import weakref


class ObjectRegistry:
    """Maps keys to weakly-referenced objects.

    register(key, obj, tags)  -- store a weak reference to obj under key,
                                  optionally associating it with tag strings
    get(key)                  -- return the live object, or None if collected
    by_tag(tag)               -- return list of live objects registered with tag
    cleanup()                 -- remove entries whose objects have been collected
    """

    def __init__(self):
        self._refs: dict[object, weakref.ref] = {}
        self._tags: dict[object, set[str]] = {}          # key -> set of tags
        self._tag_index: dict[str, set[object]] = {}     # tag -> set of keys

    def register(self, key, obj, tags: set[str] | None = None) -> None:
        """Store a weak reference to *obj* under *key*.

        Optionally associate the entry with one or more *tags*.
        """
        self._refs[key] = weakref.ref(obj)

        # Remove old tag associations if key is being re-registered
        old_tags = self._tags.pop(key, set())
        for tag in old_tags:
            self._tag_index.get(tag, set()).discard(key)

        if tags:
            self._tags[key] = set(tags)
            for tag in tags:
                if tag not in self._tag_index:
                    self._tag_index[tag] = set()
                self._tag_index[tag].add(key)
        else:
            self._tags[key] = set()

    def get(self, key):
        """Return the object stored under *key*, or None if it has been collected."""
        ref = self._refs.get(key)
        if ref is None:
            return None
        return ref()  # returns None automatically if the referent is gone

    def by_tag(self, tag: str) -> list:
        """Return a list of live objects registered with *tag*.

        Dead references are excluded from the result.
        """
        keys = self._tag_index.get(tag, set())
        result = []
        for key in keys:
            ref = self._refs.get(key)
            if ref is not None:
                obj = ref()
                if obj is not None:
                    result.append(obj)
        return result

    def cleanup(self) -> None:
        """Remove all entries whose referenced objects have been garbage-collected."""
        dead_keys = [key for key, ref in self._refs.items() if ref() is None]
        for key in dead_keys:
            del self._refs[key]
            old_tags = self._tags.pop(key, set())
            for tag in old_tags:
                self._tag_index.get(tag, set()).discard(key)

    def __len__(self) -> int:
        return len(self._refs)

    def __contains__(self, key) -> bool:
        return key in self._refs
