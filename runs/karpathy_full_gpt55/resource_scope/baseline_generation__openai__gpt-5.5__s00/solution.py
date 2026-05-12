from contextlib import ExitStack
from typing import Any


class ResourceScope:
    """Context manager that closes acquired resources in reverse order."""

    def __init__(self) -> None:
        self._stack = ExitStack()

    def __enter__(self) -> "ResourceScope":
        self._stack.__enter__()
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> bool:
        return self._stack.__exit__(exc_type, exc, traceback)

    def acquire(self, resource: Any) -> Any:
        """Record a resource to be closed on context exit and return it."""
        self._stack.callback(resource.close)
        return resource
