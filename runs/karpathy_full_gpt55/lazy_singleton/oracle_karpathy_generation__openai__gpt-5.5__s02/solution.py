import threading
from typing import Callable, Generic, TypeVar, cast

T = TypeVar("T")
_MISSING = object()


class LazySingleton(Generic[T]):
    def __init__(self, factory: Callable[[], T]) -> None:
        self._factory = factory
        self._lock = threading.Lock()
        self._value: object = _MISSING

    def get(self) -> T:
        value = self._value
        if value is _MISSING:
            with self._lock:
                value = self._value
                if value is _MISSING:
                    value = self._factory()
                    self._value = value
        return cast(T, value)
