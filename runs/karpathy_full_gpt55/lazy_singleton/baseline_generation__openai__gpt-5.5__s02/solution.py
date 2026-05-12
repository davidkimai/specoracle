from __future__ import annotations

import threading
from typing import Callable, Generic, Optional, TypeVar, cast

_T = TypeVar("_T")

_UNINITIALIZED = 0
_INITIALIZING = 1
_INITIALIZED = 2


class LazySingleton(Generic[_T]):
    __slots__ = ("_factory", "_value", "_condition", "_state", "_owner")

    def __init__(self, factory: Callable[[], _T]) -> None:
        if not callable(factory):
            raise TypeError("factory must be callable")
        self._factory: Optional[Callable[[], _T]] = factory
        self._value: Optional[_T] = None
        self._condition = threading.Condition()
        self._state = _UNINITIALIZED
        self._owner: Optional[int] = None

    def get(self) -> _T:
        current_thread = threading.get_ident()

        while True:
            with self._condition:
                if self._state == _INITIALIZED:
                    return cast(_T, self._value)

                if self._state == _UNINITIALIZED:
                    self._state = _INITIALIZING
                    self._owner = current_thread
                    break

                if self._owner == current_thread:
                    raise RuntimeError("LazySingleton factory recursively called get()")

                while self._state == _INITIALIZING:
                    self._condition.wait()

        try:
            factory = self._factory
            if factory is None:
                raise RuntimeError("LazySingleton is in an invalid state")
            value = factory()
        except BaseException:
            with self._condition:
                self._state = _UNINITIALIZED
                self._owner = None
                self._condition.notify_all()
            raise

        with self._condition:
            self._value = value
            self._factory = None
            self._state = _INITIALIZED
            self._owner = None
            self._condition.notify_all()
            return value
