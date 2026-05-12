import collections
from typing import Dict, List, Deque

class SlidingWindowLimiter:
    """
    Implements a sliding window rate limiter.

    This limiter tracks events for different keys within a specified time window.
    It allows an event if the count of events for its key within the sliding
    window is less than a given limit.
    """

    def __init__(self, limit: int, window_seconds: int):
        """
        Initializes the SlidingWindowLimiter.

        Args:
            limit: The maximum number of events allowed in the window.
                   Must be a positive integer.
            window_seconds: The duration of the sliding window in seconds.
                            Must be a positive integer.

        Raises:
            ValueError: If limit or window_seconds are not positive.
        """
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError("limit must be a positive integer")
        if not isinstance(window_seconds, int) or window_seconds <= 0:
            raise ValueError("window_seconds must be a positive integer")

        self.limit = limit
        self.window_seconds = window_seconds
        self._events: Dict[str, Deque[int]] = collections.defaultdict(collections.deque)

    def allow(self, key: str, timestamp: int) -> bool:
        """
        Determines if an event is allowed for a given key at a specific timestamp.

        If allowed, the event is recorded. Otherwise, it is not. The window is
        defined as the half-open interval (timestamp - window_seconds, timestamp].

        Args:
            key: A unique identifier for the event source.
            timestamp: The time of the event, as an integer (e.g., Unix timestamp).

        Returns:
            True if the event is within the limit and has been recorded,
            False otherwise.
        """
        timestamps = self._events[key]
        window_start_time = timestamp - self.window_seconds

        # Prune timestamps that are outside the current window.
        # Timestamps are added in increasing order, so we can efficiently
        # remove old ones from the left of the deque.
        while timestamps and timestamps[0] <= window_start_time:
            timestamps.popleft()

        # Check if the current number of events is under the limit.
        if len(timestamps) < self.limit:
            timestamps.append(timestamp)
            return True
        else:
            return False

    def snapshot(self, key: str) -> List[int]:
        """
        Returns a snapshot of the retained timestamps for a given key.

        Args:
            key: The key for which to retrieve the event timestamps.

        Returns:
            A list of integers representing the timestamps currently stored
            for the key. Returns an empty list if the key has no recorded events.
        """
        # Return a copy to prevent external modification of the internal state.
        return list(self._events.get(key, []))
