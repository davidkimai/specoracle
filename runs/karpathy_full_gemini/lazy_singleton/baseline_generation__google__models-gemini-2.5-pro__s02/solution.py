import threading
from typing import Callable, TypeVar, Optional, Generic

# A generic type variable for the singleton instance type.
T = TypeVar('T')


class LazySingleton(Generic[T]):
    """
    A thread-safe provider for a lazily-initialized singleton object.

    The singleton instance is created by the provided factory on the first
    call to get() and the same instance is returned for all subsequent calls.
    The initialization is guaranteed to be thread-safe.
    """

    def __init__(self, factory: Callable[[], T]):
        """
        Initializes the LazySingleton with a factory function.

        Args:
            factory: A callable that takes no arguments and returns the
                     singleton instance. This will be called at most once.
        """
        if not callable(factory):
            raise TypeError("factory must be a callable")
        self._factory = factory
        self._instance: Optional[T] = None
        self._lock = threading.Lock()

    def get(self) -> T:
        """
        Returns the singleton instance.

        If the instance has not been created yet, it will be created using
        the factory. This method is safe for concurrent calls from multiple
        threads.

        Returns:
            The singleton instance.
        """
        # Fast path: Check if the instance is already created without locking.
        # This avoids the overhead of acquiring a lock for every call once
        # the singleton is initialized.
        if self._instance is not None:
            return self._instance

        # Slow path: The instance is not yet created. Acquire the lock to
        # ensure that only one thread can create the instance.
        with self._lock:
            # Double-check: Another thread might have created the instance
            # while the current thread was waiting for the lock.
            if self._instance is None:
                self._instance = self._factory()

        # At this point, self._instance is guaranteed to be non-None.
        return self._instance
