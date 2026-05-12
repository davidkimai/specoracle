from __future__ import annotations

from contextlib import ExitStack
from types import TracebackType
from typing import Any


class ResourceScope:
    """Context manager that closes acquired resources in reverse order."""

    def __init__(self) -> None:
        self._exit_stack = ExitStack()
        self._closed = False

    def __enter__(self) -> "ResourceScope":
        if self._closed:
            raise RuntimeError("cannot enter a closed ResourceScope")
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        self._closed = True
        return self._exit_stack.__exit__(exc_type, exc, traceback)

    def acquire(self, resource: Any) -> Any:
        if self._closed:
            raise RuntimeError("cannot acquire resources after ResourceScope is closed")

        close = getattr(resource, "close", None)
        if not callable(close):
            raise TypeError("resource must provide a callable close() method")

        self._exit_stack.callback(close)
        return resource

    def close(self) -> None:
        if self._closed:
            return

        self._closed = True
        self._exit_stack.close()
