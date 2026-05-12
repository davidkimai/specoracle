import threading
from typing import Callable, Generic, TypeVar, cast

T = TypeVar("T")

_UNSET = object()


class LazySingleton(Generic[T]):
    """Thread-safe lazy singleton wrapper around a zero-argument factory."""

    __slots__ = ("_factory", "_lock", "_value")

    def __init__(self, factory: Callable[[], T]) -> None:
        if not callable(factory):
            raise TypeError("factory must be callable")

        self._factory = factory
        self._lock = threading.Lock()
        self._value: object = _UNSET

    def get(self) -> T:
        value = self._value
        if value is not _UNSET:
            return cast(T, value)

        with self._lock:
            value = self._value
            if value is _UNSET:
                value = self._factory()
                self._value = value

            return cast(T, value)
