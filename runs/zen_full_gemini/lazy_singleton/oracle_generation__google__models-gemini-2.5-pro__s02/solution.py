import threading
from typing import Callable, Generic, TypeVar

T = TypeVar('T')


class LazySingleton(Generic[T]):
    """
    Provides thread-safe, lazy initialization for a singleton object.

    The object is created by a provided factory function on the first call
    to get(). All subsequent calls, from any thread, will return the same
    cached object.
    """

    def __init__(self, factory: Callable[[], T]) -> None:
        """
        Initializes the LazySingleton with a factory function.

        The factory will be called at most once to create the singleton instance.

        Args:
            factory: A callable that takes no arguments and returns the object
                     to be managed as a singleton.

        Raises:
            TypeError: If the provided factory is not a callable object.
        """
        if not callable(factory):
            raise TypeError("The factory must be a callable.")

        self._factory = factory
        self._instance: T | None = None
        self._lock = threading.Lock()

    def get(self) -> T:
        """
        Returns the singleton instance, creating it if it does not exist.

        This method uses a double-checked locking pattern to ensure both
        thread safety and high performance. The lock is only acquired during
        the initial creation of the instance.

        Returns:
            The singleton instance.
        """
        # First check is performed without a lock for performance.
        # This is the fast path taken by all calls after the first one.
        if self._instance is not None:
            return self._instance

        # If the instance does not exist, acquire a lock to ensure only one
        # thread can create it.
        with self._lock:
            # The second check is necessary because another thread might have
            # created the instance while the current thread was waiting for
            # the lock.
            if self._instance is None:
                self._instance = self._factory()

        # At this point, self._instance is guaranteed to be initialized.
        return self._instance
