import weakref


class ObjectRegistry:
    def __init__(self):
        self._registry: dict[str, weakref.ref] = {}

    def register(self, key: str, obj: object) -> None:
        self._registry[key] = weakref.ref(obj)

    def get(self, key: str) -> object | None:
        ref = self._registry.get(key)
        if ref is None:
            return None
        return ref()

    def cleanup(self) -> None:
        dead_keys = [key for key, ref in self._registry.items() if ref() is None]
        for key in dead_keys:
            del self._registry[key]

    def __contains__(self, key: str) -> bool:
        ref = self._registry.get(key)
        if ref is None:
            return False
        return ref() is not None

    def __len__(self) -> int:
        return sum(1 for ref in self._registry.values() if ref() is not None)

    def keys(self):
        return [key for key, ref in self._registry.items() if ref() is not None]
