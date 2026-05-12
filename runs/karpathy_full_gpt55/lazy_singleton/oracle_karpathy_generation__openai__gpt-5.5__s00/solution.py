import threading


class LazySingleton:
    def __init__(self, factory):
        if not callable(factory):
            raise TypeError("factory must be callable")
        self._factory = factory
        self._lock = threading.Lock()
        self._created = False
        self._value = None

    def get(self):
        if not self._created:
            with self._lock:
                if not self._created:
                    self._value = self._factory()
                    self._created = True
        return self._value
