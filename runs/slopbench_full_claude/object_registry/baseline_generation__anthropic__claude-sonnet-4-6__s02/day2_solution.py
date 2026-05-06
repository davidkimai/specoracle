import weakref


class ObjectRegistry:
    def __init__(self):
        self._registry: dict[str, weakref.ref] = {}
        self._tags: dict[str, set[str]] = {}  # key -> set of tags

    def register(self, key: str, obj: object, tags: set[str] | None = None) -> None:
        """Store a weak reference to obj under key, optionally with tags."""
        self._registry[key] = weakref.ref(obj)
        self._tags[key] = set(tags) if tags else set()

    def get(self, key: str) -> object | None:
        """Return the object for key, or None if missing or garbage-collected."""
        ref = self._registry.get(key)
        if ref is None:
            return None
        obj = ref()
        return obj  # None if already collected

    def by_tag(self, tag: str) -> list[object]:
        """Return all live objects registered with the given tag."""
        result = []
        for key, tags in self._tags.items():
            if tag in tags:
                ref = self._registry.get(key)
                if ref is not None:
                    obj = ref()
                    if obj is not None:
                        result.append(obj)
        return result

    def cleanup(self) -> None:
        """Remove all entries whose referents have been garbage-collected."""
        dead_keys = [key for key, ref in self._registry.items() if ref() is None]
        for key in dead_keys:
            del self._registry[key]
            self._tags.pop(key, None)
