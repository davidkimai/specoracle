import threading


class LazySingleton:
    """Holds a single lazily-created instance produced by *factory*.

    The instance is created on the first call to ``get()`` and reused on
    every subsequent call.  Creation is thread-safe: *factory* is called
    exactly once even when multiple threads race to call ``get()``
    simultaneously.
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
