"""
TTLCache: a cache with time-to-live expiry and LRU eviction.
"""

import time
from collections import OrderedDict


class TTLCache:
    """
    A cache that evicts entries after a TTL expires and uses LRU eviction
    when the maximum size is exceeded.

    Parameters
    ----------
    max_size : int
        Maximum number of entries the cache may hold at one time.
    ttl_seconds : float
        Number of seconds an entry remains valid after being set.
    now : callable, optional
        Zero-argument callable that returns the current time as a float
        (seconds).  Defaults to ``time.monotonic``.  Useful for testing.
    """

    def __init__(self, max_size: int, ttl_seconds: float, *, now=None):
        if max_size < 1:
            raise ValueError("max_size must be at least 1")
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")

        self._max_size = max_size
        self._ttl = ttl_seconds
        self._now = now if now is not None else time.monotonic

        # OrderedDict used as an ordered map: key -> (value, expire_at)
        # Most-recently-used entries are moved to the end (right side).
        self._cache: OrderedDict = OrderedDict()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set(self, key, value) -> None:
        """Store *value* under *key*, resetting its TTL."""
        current = self._now()
        expire_at = current + self._ttl

        if key in self._cache:
            # Remove so we can re-insert at the end (mark as most-recent).
            del self._cache[key]

        self._cache[key] = (value, expire_at)

        # Evict expired entries first, then LRU if still over capacity.
        self._evict_expired(current)
        while len(self._cache) > self._max_size:
            # popitem(last=False) removes the least-recently-used entry.
            self._cache.popitem(last=False)

    def get(self, key):
        """
        Return the value stored under *key*, or ``None`` if the key is
        absent or its TTL has elapsed.
        """
        if key not in self._cache:
            return None

        value, expire_at = self._cache[key]
        current = self._now()

        if current >= expire_at:
            # Entry has expired; remove it.
            del self._cache[key]
            return None

        # Mark as most-recently used.
        self._cache.move_to_end(key)
        return value

    def warm(self, initial: dict) -> None:
        """
        Pre-populate the cache from *initial*, a plain dict mapping keys to
        values.  Each entry is inserted in iteration order using the current
        time as the start of its TTL.  If the number of entries in *initial*
        exceeds *max_size*, only the latest-inserted entries are kept (i.e.
        earlier entries are evicted by the normal LRU rule).
        """
        for key, value in initial.items():
            self.set(key, value)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _evict_expired(self, current: float) -> None:
        """Remove all entries whose TTL has elapsed as of *current*."""
        expired_keys = [k for k, (_, exp) in self._cache.items() if current >= exp]
        for k in expired_keys:
            del self._cache[k]

    # ------------------------------------------------------------------
    # Convenience / introspection
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        """Return the number of entries currently in the cache (including
        potentially expired ones that have not yet been evicted)."""
        return len(self._cache)

    def __contains__(self, key) -> bool:
        """Return True if *key* is present and not expired."""
        return self.get(key) is not None

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"TTLCache(max_size={self._max_size}, ttl_seconds={self._ttl}, "
            f"entries={len(self._cache)})"
        )
