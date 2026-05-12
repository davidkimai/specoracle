# -*- coding: utf-8 -*-
"""
A thread-unsafe sliding window rate limiter implementation.
"""

import collections
from typing import Dict, List, Deque

__all__ = ["SlidingWindowLimiter"]


class SlidingWindowLimiter:
    """
    Implements a sliding window rate limiter.

    This limiter tracks event timestamps for each key within a specified time
    window to enforce a limit on the number of events. It is not thread-safe.
    """

    def __init__(self, limit: int, window_seconds: int):
        """
        Initializes the SlidingWindowLimiter.

        Args:
            limit: The maximum number of events allowed in the window. Must be
                   a positive integer.
            window_seconds: The duration of the sliding window in seconds. Must be
                            a positive integer.

        Raises:
            ValueError: If limit or window_seconds are not positive integers.
        """
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError("limit must be a positive integer")
        if not isinstance(window_seconds, int) or window_seconds <= 0:
            raise ValueError("window_seconds must be a positive integer")

        self.limit = limit
        self.window_seconds = window_seconds
        self._storage: Dict[str, Deque[int]] = collections.defaultdict(
            collections.deque
        )

    def allow(self, key: str, timestamp: int) -> bool:
        """
        Determines if an event is allowed and records it if so.

        An event is allowed if the count of events for the given key within the
        half-open time window (timestamp - window_seconds, timestamp] is less
        than the configured limit.

        Args:
            key: A unique identifier for the entity being rate-limited.
            timestamp: The integer timestamp of the event (e.g., Unix time).

        Returns:
            True if the event is allowed and recorded, False otherwise.
        """
        timestamps = self._storage[key]
        window_start_time = timestamp - self.window_seconds

        # Prune timestamps that are older than the start of the window.
        # The window is (window_start_time, timestamp]. Timestamps equal to
        # window_start_time are outside the window and should be removed.
        while timestamps and timestamps[0] <= window_start_time:
            timestamps.popleft()

        # Check if adding the new event would exceed the limit.
        if len(timestamps) < self.limit:
            timestamps.append(timestamp)
            return True

        return False

    def snapshot(self, key: str) -> List[int]:
        """
        Returns a snapshot of the retained timestamps for a given key.

        Args:
            key: The key for which to retrieve the timestamps.

        Returns:
            A new list containing the timestamps currently stored for the key.
            Returns an empty list if the key has no recorded events.
        """
        # Return a copy to prevent external modification of the internal deque.
        return list(self._storage.get(key, collections.deque()))
