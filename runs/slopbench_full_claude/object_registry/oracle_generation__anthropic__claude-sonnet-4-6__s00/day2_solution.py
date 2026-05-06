import weakref


class ObjectRegistry:
    """Registry that holds weak references to objects."""

    def __init__(self):
        self._store: dict[object, weakref.ref] = {}
        self._tags: dict[object, set[str]] = {}
        self._tag_index: dict[str, set[object]] = {}

    def register(self, key, obj, tags: set[str] | None = None) -> None:
        """Store a weak reference to *obj* under *key*, optionally with *tags*."""
        self._store[key] = weakref.ref(obj)
        # Update tag mappings
        old_tags = self._tags.pop(key, set())
        for tag in old_tags:
            self._tag_index.get(tag, set()).discard(key)
        new_tags = set(tags) if tags is not None else set()
        self._tags[key] = new_tags
        for tag in new_tags:
            if tag not in self._tag_index:
                self._tag_index[tag] = set()
            self._tag_index[tag].add(key)

    def get(self, key):
        """Return the object for *key*, or None if absent or garbage-collected."""
        ref = self._store.get(key)
        if ref is None:
            return None
        return ref()

    def by_tag(self, tag: str) -> list:
        """Return all live objects registered with *tag*."""
        keys = self._tag_index.get(tag, set())
        result = []
        for key in keys:
            ref = self._store.get(key)
            if ref is not None:
                obj = ref()
                if obj is not None:
                    result.append(obj)
        return result

    def cleanup(self) -> None:
        """Remove entries whose referents have been garbage-collected."""
        dead_keys = [key for key, ref in self._store.items() if ref() is None]
        for key in dead_keys:
            del self._store[key]
            old_tags = self._tags.pop(key, set())
            for tag in old_tags:
                self._tag_index.get(tag, set()).discard(key)
