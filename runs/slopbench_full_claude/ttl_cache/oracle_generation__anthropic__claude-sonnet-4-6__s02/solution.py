"""
TTLCache: a cache with time-to-live expiry and LRU eviction.
"""

import time
from collections import OrderedDict


class TTLCache:
    """
    A fixed-capacity cache that evicts entries by LRU policy when full
    and also expires entries after ``ttl_seconds``.

    Parameters
    ----------
    max_size : int
        Maximum number of entries held at one time.
    ttl_seconds : float
        Seconds after which a stored entry is considered expired.
    now : callable, optional
        Zero-argument callable returning the current time as a float.
        Defaults to ``time.monotonic``.  Useful for testing.
    """

    def __init__(self, max_size: int, ttl_seconds: float, *, now=None):
        if max_size < 1:
            raise ValueError(f"max_size must be at least 1, got {max_size!r}")
        if ttl_seconds <= 0:
            raise ValueError(f"ttl_seconds must be positive, got {ttl_seconds!r}")

        self._max_size = max_size
        self._ttl = ttl_seconds
        self._now = now if now is not None else time.monotonic
        # Maps key -> (value, expiry_time); OrderedDict preserves insertion /
        # access order so the leftmost entry is the least-recently used.
        self._store: OrderedDict = OrderedDict()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def set(self, key, value) -> None:
        """Store *value* under *key*, evicting LRU entry if necessary."""
        expiry = self._now() + self._ttl

        if key in self._store:
            # Refresh position to most-recently used.
            self._store.move_to_end(key)
            self._store[key] = (value, expiry)
            return

        self._store[key] = (value, expiry)

        # Evict until we are within capacity.  We may need to evict more than
        # one entry if expired entries were not cleaned up earlier.
        while len(self._store) > self._max_size:
            self._store.popitem(last=False)

    def get(self, key):
        """
        Return the value stored under *key*, or ``None`` if absent or expired.

        A hit moves the entry to the most-recently-used position.
        """
        if key not in self._store:
            return None

        value, expiry = self._store[key]

        if self._now() >= expiry:
            del self._store[key]
            return None

        # Mark as most-recently used.
        self._store.move_to_end(key)
        return value

    # ------------------------------------------------------------------
    # Convenience / introspection
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        """Number of entries currently stored (including not-yet-expired ones)."""
        return len(self._store)

    def __contains__(self, key) -> bool:
        """Return True if *key* is present and not expired."""
        return self.get(key) is not None

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"max_size={self._max_size}, "
            f"ttl_seconds={self._ttl}, "
            f"entries={len(self._store)})"
        )
