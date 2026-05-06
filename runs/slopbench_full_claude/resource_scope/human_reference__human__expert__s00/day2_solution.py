from __future__ import annotations


class ResourceScope:
    def __init__(self) -> None:
        self._resources: list[object] = []

    def __enter__(self):
        return self

    def acquire(self, resource):
        self._resources.append(resource)
        return resource

    def release(self, resource):
        try:
            self._resources.remove(resource)
        except ValueError:
            raise ValueError(f"Resource {resource!r} is not tracked by this scope")
        close = getattr(resource, 'close', None)
        if close is not None:
            close()

    def __exit__(self, exc_type, exc, tb) -> bool:
        while self._resources:
            resource = self._resources.pop()
            close = getattr(resource, 'close', None)
            if close is not None:
                close()
        return False
