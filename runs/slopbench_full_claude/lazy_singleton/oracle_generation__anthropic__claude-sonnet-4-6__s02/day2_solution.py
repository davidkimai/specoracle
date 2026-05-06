import threading


class LazySingleton:
    """Lazily creates a single instance using the provided factory callable.

    The instance is created on the first call to get() and reused on all
    subsequent calls. Thread-safe via double-checked locking.
    """

    def __init__(self, factory):
        if not callable(factory):
            raise TypeError(f"factory must be callable, got {type(factory)!r}")
        self._factory = factory
        self._instance = None
        self._lock = threading.Lock()

    def get(self):
        if self._instance is None:
            with self._lock:
                if self._instance is None:
                    self._instance = self._factory()
        return self._instance

    def reset_for_test(self):
        """Restore the uninitialized state so the next get() creates a fresh object.

        Acquires the lock before clearing the instance to preserve thread safety.
        """
        with self._lock:
            self._instance = None
