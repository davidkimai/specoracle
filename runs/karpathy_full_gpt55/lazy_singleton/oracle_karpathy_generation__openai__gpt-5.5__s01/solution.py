import threading
from typing import Callable, Generic, TypeVar, cast

T = TypeVar("T")


class LazySingleton(Generic[T]):
    """Thread-safe lazy singleton.

    Assumptions:
    - factory is a zero-argument callable.
    - if factory raises, the exception is not cached and a later get() may retry.
    """

    __slots__ = ("_factory", "_lock", "_unset", "_value")

    def __init__(self, factory: Callable[[], T]) -> None:
        if not callable(factory):
            raise TypeError("factory must be callable")
        self._factory = factory
        self._lock = threading.Lock()
        self._unset = object()
        self._value = self._unset

    def get(self) -> T:
        value = self._value
        if value is self._unset:
            with self._lock:
                value = self._value
                if value is self._unset:
                    value = self._factory()
                    self._value = value
        return cast(T, value)
