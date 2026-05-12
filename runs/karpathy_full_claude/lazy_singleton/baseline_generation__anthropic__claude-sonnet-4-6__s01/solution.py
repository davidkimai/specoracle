import threading


class LazySingleton:
    def __init__(self, factory):
        self._factory = factory
        self._instance = None
        self._lock = threading.Lock()

    def get(self):
        if self._instance is None:
            with self._lock:
                if self._instance is None:
                    self._instance = self._factory()
        return self._instance
