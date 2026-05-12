from contextlib import ExitStack
from typing import Any


class ResourceScope:
    """Context manager that closes acquired resources in reverse order."""

    def __init__(self) -> None:
        self._stack = ExitStack()
        self._active = False

    def __enter__(self) -> "ResourceScope":
        if self._active:
            raise RuntimeError("ResourceScope is already active")
        self._active = True
        self._stack.__enter__()
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
        try:
            return self._stack.__exit__(exc_type, exc, tb)
        finally:
            self._active = False

    def acquire(self, resource: Any) -> Any:
        if not self._active:
            raise RuntimeError("resources may only be acquired inside an active ResourceScope")

        close = getattr(resource, "close")
        self._stack.callback(close)
        return resource

    def close(self) -> None:
        self.__exit__(None, None, None)
