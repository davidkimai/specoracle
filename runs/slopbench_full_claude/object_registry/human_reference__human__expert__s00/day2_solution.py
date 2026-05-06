from __future__ import annotations

import weakref
from typing import Any


class ObjectRegistry:
    def __init__(self) -> None:
        self._refs: dict[str, weakref.ReferenceType[Any]] = {}
        self._tags: dict[str, set[str]] = {}  # key -> set of tags

    def register(self, key: str, obj: object, tags: set[str] | None = None) -> None:
        self._refs[key] = weakref.ref(obj)
        self._tags[key] = set(tags) if tags is not None else set()

    def get(self, key: str):
        ref = self._refs.get(key)
        return None if ref is None else ref()

    def cleanup(self) -> None:
        dead = {key for key, ref in self._refs.items() if ref() is None}
        for key in dead:
            del self._refs[key]
            self._tags.pop(key, None)

    def by_tag(self, tag: str) -> list[Any]:
        result = []
        for key, ref in self._refs.items():
            if tag in self._tags.get(key, set()):
                obj = ref()
                if obj is not None:
                    result.append(obj)
        return result
