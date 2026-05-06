import weakref


class ObjectRegistry:
    def __init__(self):
        self._registry: dict[str, weakref.ref] = {}
        self._tags: dict[str, set[str]] = {}  # key -> set of tags

    def register(self, key: str, obj: object, tags: set[str] | None = None) -> None:
        self._registry[key] = weakref.ref(obj)
        self._tags[key] = set(tags) if tags else set()

    def get(self, key: str) -> object | None:
        ref = self._registry.get(key)
        if ref is None:
            return None
        return ref()

    def by_tag(self, tag: str) -> list[object]:
        result = []
        for key, key_tags in self._tags.items():
            if tag in key_tags:
                ref = self._registry.get(key)
                if ref is not None:
                    obj = ref()
                    if obj is not None:
                        result.append(obj)
        return result

    def cleanup(self) -> None:
        dead_keys = [key for key, ref in self._registry.items() if ref() is None]
        for key in dead_keys:
            del self._registry[key]
            self._tags.pop(key, None)
