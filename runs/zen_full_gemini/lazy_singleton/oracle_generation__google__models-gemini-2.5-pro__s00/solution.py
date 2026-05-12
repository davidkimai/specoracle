import threading
from typing import Callable, TypeVar, Generic

T = TypeVar('T')

class LazySingleton(Generic[T]):
    """
    Manages a lazily-initialized, thread-safe singleton object.

    The object is created by a provided factory on the first call to get().
    Subsequent calls return the same cached instance. The initialization is
    guaranteed to happen only once, even if multiple threads call get()
    concurrently.
    """

    _sentinel = object()

    def __init__(self, factory: Callable[[], T]):
        """
        Initializes the LazySingleton with a factory function.

        Args:
            factory: A callable that takes no arguments and returns the
                     object to be managed as a singleton.

        Raises:
            TypeError: If the provided factory is not a callable object.
        """
        if not callable(factory):
            raise TypeError("The factory must be a callable.")

        self._factory = factory
        self._instance: object = self._sentinel
        self._lock = threading.Lock()

    def get(self) -> T:
        """
        Returns the singleton instance, creating it if it does not exist.

        This method employs a double-checked locking pattern to ensure that
        the factory is called at most once, in a thread-safe manner, while
        minimizing lock contention for subsequent accesses.

        Returns:
            The singleton instance of type T.
        """
        # First check avoids the overhead of acquiring a lock on every call.
        if self._instance is not self._sentinel:
            return self._instance  # type: ignore[return-value]

        with self._lock:
            # Second check handles the race condition where multiple threads
            # might have passed the first check simultaneously. Only the
            # first thread to acquire the lock will create the instance.
            if self._instance is self._sentinel:
                self._instance = self._factory()

        return self._instance  # type: ignore[return-value]
