# -*- coding: utf-8 -*-
"""
A thread-safe, lazy singleton provider.

This module provides a class `LazySingleton` that encapsulates the logic for
creating and retrieving a single, lazily-initialized object in a thread-safe
manner.
"""

import threading
from typing import Callable, TypeVar, Generic, cast

# A unique sentinel object to detect if the instance has been created.
# This is more robust than using `None`, in case the factory can legitimately
# return `None` as the singleton instance.
_SENTINEL = object()

# A generic type variable to represent the type of the singleton instance.
T = TypeVar('T')


class LazySingleton(Generic[T]):
    """
    Provides a thread-safe, lazily-initialized singleton instance.

    The factory function is called at most once, on the first call to `get()`,
    and the same object is returned for all subsequent calls. The initialization
    is protected by a lock to ensure thread safety.
    """

    def __init__(self, factory: Callable[[], T]):
        """
        Initializes the LazySingleton with a factory function.

        Args:
            factory: A callable that takes no arguments and returns the object
                     to be created as a singleton.

        Raises:
            TypeError: If the provided factory is not a callable.
        """
        if not callable(factory):
            raise TypeError("The factory must be a callable.")

        self._factory = factory
        self._instance: object = _SENTINEL
        self._lock = threading.Lock()

    def get(self) -> T:
        """
        Returns the singleton instance, creating it if necessary.

        This method is thread-safe. If multiple threads call it simultaneously
        before the instance is created, the factory will be executed only once.
        All threads will receive the same instance.

        The implementation uses a double-checked locking pattern to avoid the
        overhead of acquiring a lock on every call after initialization.

        Returns:
            The singleton instance.
        """
        # Fast path: check if the instance is already created without locking.
        # This avoids the overhead of acquiring a lock on every call after
        # the first one. The read of `self._instance` is atomic.
        if self._instance is not _SENTINEL:
            return cast(T, self._instance)

        # Slow path: acquire the lock to ensure only one thread creates the
        # instance.
        with self._lock:
            # Double-check: another thread might have created the instance
            # while this thread was waiting for the lock.
            if self._instance is _SENTINEL:
                self._instance = self._factory()

        return cast(T, self._instance)
