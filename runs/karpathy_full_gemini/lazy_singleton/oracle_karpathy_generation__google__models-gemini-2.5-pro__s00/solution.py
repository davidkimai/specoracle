"""
A thread-safe, lazy singleton implementation.
"""

import threading
from typing import Callable, Generic, TypeVar

T = TypeVar('T')


class LazySingleton(Generic[T]):
    """
    A container for a lazily-initialized, thread-safe singleton object.

    The object is created by a provided factory function on the first call
    to get(). Subsequent calls to get() will return the same object.
    """

    def __init__(self, factory: Callable[[], T]):
        """
        Initializes the LazySingleton with a factory function.

        Args:
            factory: A callable that takes no arguments and returns the
                     object to be managed as a singleton.
        """
        if not callable(factory):
            raise TypeError("factory must be a callable")
        self._factory = factory
        self._instance: T | None = None
        self._lock = threading.Lock()

    def get(self) -> T:
        """
        Returns the singleton instance, creating it if it doesn't exist.

        This method is thread-safe. If multiple threads call get()
        concurrently when the instance has not yet been created, the factory
        will be called exactly once, and all threads will receive the same
        instance.
        """
        # The Double-Checked Locking pattern is used here for efficient and
        # thread-safe lazy initialization.

        # First check (without a lock): A fast path for the common case where
        # the instance has already been initialized. This avoids the overhead
        # of acquiring a lock on every call.
        if self._instance is None:
            # Acquire the lock only when the instance might need to be created.
            # The 'with' statement ensures the lock is always released.
            with self._lock:
                # Second check (inside the lock): It's crucial to check again
                # because another thread might have acquired the lock and
                # created the instance while the current thread was waiting.
                if self._instance is None:
                    self._instance = self._factory()

        # At this point, self._instance is guaranteed to be initialized and of
        # type T. An assertion helps static analysis tools and provides a
        # runtime sanity check, although the logic itself ensures this.
        assert self._instance is not None
        return self._instance
