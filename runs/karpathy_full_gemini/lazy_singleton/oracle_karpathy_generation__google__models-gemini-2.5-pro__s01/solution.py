import threading
from typing import Callable, TypeVar, Generic

T = TypeVar('T')

_SENTINEL = object()


class LazySingleton(Generic[T]):
    """
    A thread-safe lazy singleton provider.

    The singleton instance is created by the provided factory function on the first
    call to get(). Subsequent calls to get() return the same instance. This
    implementation uses a double-checked locking pattern for efficiency.
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
        Returns the singleton instance.

        The factory is called to create the instance on the first call to this
        method. The operation is thread-safe. If multiple threads call get()
        simultaneously when the instance is not yet created, the factory will
        be invoked only once.
        """
        # First check (fast path) avoids acquiring the lock on every call
        # once the instance is initialized.
        if self._instance is not _SENTINEL:
            return self._instance  # type: ignore

        with self._lock:
            # Second check is necessary because another thread might have
            # acquired the lock and created the instance while the current
            # thread was waiting to acquire the lock.
            if self._instance is _SENTINEL:
                self._instance = self._factory()

        return self._instance  # type: ignore
