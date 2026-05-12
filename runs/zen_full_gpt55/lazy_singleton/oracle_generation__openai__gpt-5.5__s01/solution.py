import threading
from typing import Callable, Generic, TypeVar

T = TypeVar("T")
_UNSET = object()


class LazySingleton(Generic[T]):
    def __init__(self, factory: Callable[[], T]) -> None:
        if not callable(factory):
            raise TypeError("factory must be callable")

        self._factory = factory
        self._lock = threading.Lock()
        self._value: object = _UNSET

    def get(self) -> T:
        with self._lock:
            if self._value is _UNSET:
                self._value = self._factory()
            return self._value  # type: ignore[return-value]
