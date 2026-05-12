import threading


class BoundedCounter:
    def __init__(self, max_total: int):
        if type(max_total) is not int or max_total <= 0:
            raise ValueError("max_total must be positive")
        self._max_total = max_total
        self._total = 0
        self._counts: dict[str, int] = {}
        self._lock = threading.Lock()

    def increment(self, name: str) -> int:
        with self._lock:
            if self._total >= self._max_total:
                raise OverflowError("maximum total count exceeded")
            new_value = self._counts.get(name, 0) + 1
            self._counts[name] = new_value
            self._total += 1
            return new_value

    def total(self) -> int:
        with self._lock:
            return self._total

    def snapshot(self) -> dict[str, int]:
        with self._lock:
            return dict(self._counts)
