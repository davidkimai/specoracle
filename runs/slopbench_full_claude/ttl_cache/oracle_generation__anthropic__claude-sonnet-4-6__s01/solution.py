"""
TTLCache: a time-aware, size-bounded cache with LRU eviction.
"""

import time
from collections import OrderedDict


class TTLCache:
    """A cache with per-entry TTL expiry and LRU eviction on overflow.

    Parameters
    ----------
    max_size:
        Maximum number of entries to hold at once.  Must be >= 1.
    ttl_seconds:
        Seconds after insertion before an entry is considered expired.
        Must be > 0.
    now:
        Optional callable returning the current time as a float (seconds).
        Defaults to ``time.monotonic``.  Useful for testing.
    """

    def __init__(self, max_size: int, ttl_seconds: float, *, now=None):
        if max_size < 1:
            raise ValueError(f"max_size must be >= 1, got {max_size!r}")
        if ttl_seconds <= 0:
            raise ValueError(f"ttl_seconds must be > 0, got {ttl_seconds!r}")

        self._max_size = max_size
        self._ttl = ttl_seconds
        self._now = now if now is not None else time.monotonic
        # Maps key -> (value, expiry_time).  Insertion/access order tracked.
        self._store: OrderedDict = OrderedDict()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def set(self, key, value) -> None:
        """Store *value* under *key*, evicting stale or LRU entries as needed."""
        expiry = self._now() + self._ttl

        if key in self._store:
            # Refresh position to most-recently-used end.
            self._store.move_to_end(key)
        self._store[key] = (value, expiry)

        self._evict_expired()
        self._evict_lru_if_over_limit()

    def get(self, key):
        """Return the value for *key*, or ``None`` if absent or expired."""
        entry = self._store.get(key)
        if entry is None:
            return None

        value, expiry = entry
        if self._now() >= expiry:
            del self._store[key]
            return None

        # Mark as most-recently used.
        self._store.move_to_end(key)
        return value

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _evict_expired(self) -> None:
        """Remove all entries whose TTL has elapsed."""
        now = self._now()
        expired_keys = [k for k, (_, exp) in self._store.items() if now >= exp]
        for key in expired_keys:
            del self._store[key]

    def _evict_lru_if_over_limit(self) -> None:
        """Drop the least-recently-used entry until size is within budget."""
        while len(self._store) > self._max_size:
            self._store.popitem(last=False)

    # ------------------------------------------------------------------
    # Dunder helpers for transparency / debugging
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self._store)

    def __repr__(self) -> str:
        return (
            f"TTLCache(max_size={self._max_size}, ttl_seconds={self._ttl}, "
            f"entries={len(self._store)})"
        )
