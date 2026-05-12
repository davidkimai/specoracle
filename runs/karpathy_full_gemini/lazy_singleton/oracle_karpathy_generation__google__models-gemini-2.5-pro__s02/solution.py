import threading
from typing import Callable, TypeVar, Generic, Optional

T = TypeVar('T')

class LazySingleton(Generic[T]):
    """
    A thread-safe lazy singleton provider.

    This class takes a factory function during initialization. The first time
    the `get()` method is called, it invokes the factory to create an object.
    Subsequent calls to `get()` return the same, cached object. The creation
    is guaranteed to happen only once, even if multiple threads call `get()`
    concurrently.

    This implementation uses a double-checked locking pattern to ensure
    thread safety with minimal performance overhead.
    """

    def __init__(self, factory: Callable[[], T]):
        """
        Initializes the LazySingleton with a factory function.

        Args:
            factory: A callable that takes no arguments and returns the object
                     to be created as a singleton.
        """
        self._factory = factory
        self._instance: Optional[T] = None
        self._lock = threading.Lock()

    def get(self) -> T:
        """
        Returns the singleton instance, creating it if necessary.

        The first call to this method will trigger the execution of the factory
        function provided at initialization. All subsequent calls will return
        the cached instance. This method is thread-safe.

        Returns:
            The singleton instance.
        """
        # First check (without lock) for performance. In the common case where
        # the instance is already created, we avoid the overhead of acquiring
        # the lock.
        if self._instance is None:
            with self._lock:
                # Second check (with lock) for correctness. This is crucial
                # to prevent a race condition where multiple threads pass the
                # first check and queue for the lock. Only the first thread
                # to acquire the lock should create the instance.
                if self._instance is None:
                    self._instance = self._factory()

        # At this point, `_instance` is guaranteed to have been created and
        # assigned. The assertion helps static analysis tools understand this.
        assert self._instance is not None
        return self._instance
