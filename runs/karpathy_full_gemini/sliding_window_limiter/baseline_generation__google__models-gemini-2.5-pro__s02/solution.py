import collections
from typing import Deque, Dict, List


class SlidingWindowLimiter:
    """
    Implements a sliding window rate limiter.

    This limiter tracks events per key within a specified time window. It allows
    an event if the count of events for that key within the sliding window is
    less than a given limit.
    """

    def __init__(self, limit: int, window_seconds: int):
        """
        Initializes the SlidingWindowLimiter.

        Args:
            limit: The maximum number of allowed events in the window.
                   Must be a positive integer.
            window_seconds: The duration of the sliding window in seconds.
                            Must be a positive integer.

        Raises:
            ValueError: If limit or window_seconds are not positive integers.
        """
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError("limit must be a positive integer")
        if not isinstance(window_seconds, int) or window_seconds <= 0:
            raise ValueError("window_seconds must be a positive integer")

        self._limit: int = limit
        self._window_seconds: int = window_seconds
        self._events: Dict[str, Deque[int]] = collections.defaultdict(
            collections.deque
        )

    def allow(self, key: str, timestamp: int) -> bool:
        """
        Determines if an event should be allowed for a given key.

        If the event is allowed, it is recorded. The window is defined as the
        half-open interval (timestamp - window_seconds, timestamp].

        Args:
            key: A unique identifier for the entity being rate-limited.
            timestamp: The time of the event, as an integer (e.g., Unix timestamp).

        Returns:
            True if the event is allowed and recorded, False otherwise.
        """
        timestamps = self._events[key]
        window_start = timestamp - self._window_seconds

        # Prune timestamps that are older than the start of the window.
        # The left of the deque contains the oldest timestamps.
        while timestamps and timestamps[0] <= window_start:
            timestamps.popleft()

        # Check if the number of events in the window is below the limit.
        if len(timestamps) < self._limit:
            timestamps.append(timestamp)
            return True

        return False

    def snapshot(self, key: str) -> List[int]:
        """
        Returns a snapshot of the retained timestamps for a given key.

        Args:
            key: The key for which to retrieve the timestamps.

        Returns:
            A list of integer timestamps currently stored for the key. An empty
            list is returned if the key has no recorded events.
        """
        return list(self._events[key])
