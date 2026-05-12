import threading
from typing import Callable, Generic, TypeVar

T = TypeVar("T")


_UNSET = object()


class LazySingleton(Generic[T]):
    """Thread-safe lazy singleton wrapper around a factory callable."""

    __slots__ = ("_factory", "_instance", "_lock")

    def __init__(self, factory: Callable[[], T]) -> None:
        if not callable(factory):
            raise TypeError("factory must be callable")
        self._factory = factory
        self._instance = _UNSET
        self._lock = threading.Lock()

    def get(self) -> T:
        instance = self._instance
        if instance is not _UNSET:
            return instance  # type: ignore[return-value]

        with self._lock:
            instance = self._instance
            if instance is _UNSET:
                instance = self._factory()
                self._instance = instance
            return instance  # type: ignore[return-value]
