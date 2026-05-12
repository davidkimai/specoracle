import threading
from typing import Callable, Generic, Optional, TypeVar, cast

T = TypeVar("T")
_MISSING = object()


class LazySingleton(Generic[T]):
    """Thread-safe lazy singleton wrapper for a zero-argument factory."""

    __slots__ = ("_factory", "_lock", "_value")

    def __init__(self, factory: Callable[[], T]) -> None:
        if not callable(factory):
            raise TypeError("factory must be callable")

        self._factory: Optional[Callable[[], T]] = factory
        self._lock = threading.Lock()
        self._value: object = _MISSING

    def get(self) -> T:
        with self._lock:
            if self._value is _MISSING:
                factory = self._factory
                if factory is None:
                    raise RuntimeError("singleton factory is not available")

                self._value = factory()
                self._factory = None

            return cast(T, self._value)
