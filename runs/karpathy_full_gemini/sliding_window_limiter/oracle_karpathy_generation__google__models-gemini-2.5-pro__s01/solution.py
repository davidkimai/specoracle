import collections
from typing import Deque, Dict, List


class SlidingWindowLimiter:
    """
    Implements a sliding window rate limiter.

    This class tracks events for different keys and determines whether a new
    event should be allowed based on a fixed limit within a sliding time window.
    """

    def __init__(self, limit: int, window_seconds: int):
        """
        Initializes the SlidingWindowLimiter.

        Args:
            limit: The maximum number of events allowed in a window. Must be a
                   positive integer.
            window_seconds: The duration of the sliding window in seconds. Must
                            be a positive integer.

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
        Determines if an event is allowed for a given key at a timestamp.

        If the number of events for the key in the half-open window
        (timestamp - window_seconds, timestamp] is less than the limit, the
        event is allowed and its timestamp is recorded. Otherwise, the event
        is denied and not recorded.

        Args:
            key: A unique string identifier for the entity being limited.
            timestamp: The integer timestamp of the event.

        Returns:
            True if the event is allowed, False otherwise.
        """
        timestamps = self._storage[key]
        window_start = timestamp - self.window_seconds

        # Remove timestamps that are outside the current window.
        # Timestamps are stored in increasing order, so we can efficiently
        # remove old ones from the left of the deque.
        while timestamps and timestamps[0] <= window_start:
            timestamps.popleft()

        # Check if the current number of events is under the limit.
        if len(timestamps) < self.limit:
            timestamps.append(timestamp)
            return True
        
        return False

    def snapshot(self, key: str) -> List[int]:
        """
        Returns a snapshot of the timestamps currently stored for a key.

        Args:
            key: The key for which to get the snapshot.

        Returns:
            A list of retained timestamps for the given key. Returns an empty
            list if the key has no recorded events.
        """
        # Return a copy to prevent modification of the internal state.
        return list(self._storage.get(key, []))
