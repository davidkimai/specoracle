import threading


class LazySingleton:
    """Holds a single lazily-created instance produced by *factory*.

    The instance is created on the first call to :meth:`get` and reused on
    every subsequent call.  Creation is thread-safe: *factory* is called at
    most once even when multiple threads race to call :meth:`get`.

    :meth:`reset_for_test` restores the uninitialized state so the next
    :meth:`get` call creates a fresh object.  It is also thread-safe.
    """

    def __init__(self, factory):
        if not callable(factory):
            raise TypeError(f"factory must be callable, got {type(factory)!r}")
        self._factory = factory
        self._instance = None
        self._lock = threading.Lock()

    def get(self):
        """Return the singleton instance, creating it on the first call."""
        if self._instance is not None:
            return self._instance
        with self._lock:
            if self._instance is None:
                self._instance = self._factory()
        return self._instance

    def reset_for_test(self):
        """Restore uninitialized state so the next get() creates a fresh object.

        Intended for test teardown only.  Thread-safe: holds the lock while
        clearing the stored instance.
        """
        with self._lock:
            self._instance = None
