# -*- coding: utf-8 -*-
"""
A thread-safe, lazy-initialized singleton provider.
"""

import threading
from typing import Callable, TypeVar, Generic

T = TypeVar('T')

# A unique sentinel object to detect if the instance has been created.
# This is used instead of None to allow the factory to return None.
_SENTINEL = object()


class LazySingleton(Generic[T]):
    """
    Provides a thread-safe, lazy-initialized singleton instance.

    The factory function is called at most once, on the first call to get().
    Subsequent calls to get() return the same cached instance. This is safe
    to use from multiple threads concurrently.

    Example:
        class ExpensiveObject:
            def __init__(self):
                print("Creating expensive object...")
                # ... time-consuming setup ...

        # The factory is just a callable that returns the object.
        singleton_provider = LazySingleton(ExpensiveObject)

        # The ExpensiveObject is not created yet.
        # It will be created on the first call to get().
        instance1 = singleton_provider.get()

        # This call will not create a new object, but return the existing one.
        instance2 = singleton_provider.get()

        assert instance1 is instance2
    """

    def __init__(self, factory: Callable[[], T]):
        """
        Initializes the LazySingleton.

        Args:
            factory: A callable that takes no arguments and returns the
                     object to be instantiated as a singleton.
        """
        if not callable(factory):
            raise TypeError("factory must be a callable")
        self._factory = factory
        self._instance: T | object = _SENTINEL
        self._lock = threading.Lock()

    def get(self) -> T:
        """
        Returns the singleton instance, creating it if necessary.

        This method is thread-safe. It uses a double-checked locking pattern
        to ensure the factory is called only once while minimizing lock
        contention.
        """
        # First check (without lock) for performance.
        # In the common case where the instance is already created,
        # we can avoid the overhead of acquiring a lock.
        if self._instance is _SENTINEL:
            with self._lock:
                # Second check (with lock) to prevent race conditions.
                # Another thread might have created the instance between the
                # first check and acquiring the lock.
                if self._instance is _SENTINEL:
                    self._instance = self._factory()

        # At this point, self._instance is guaranteed to be of type T.
        # We can safely cast it for static type checkers.
        return self._instance  # type: ignore
