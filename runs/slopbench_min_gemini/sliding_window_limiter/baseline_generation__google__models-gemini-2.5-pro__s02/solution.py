import collections
from typing import Deque, Dict, List

class SlidingWindowLimiter:
    """
    A rate limiter using the sliding window algorithm.

    This class tracks event timestamps for different keys and enforces a limit
    on the number of events that can occur within a specified time window.
    """

    def __init__(self, limit: int, window_seconds: int):
        """
        Initializes the SlidingWindowLimiter.

        Args:
            limit: The maximum number of events allowed in the window. Must be
                   a positive integer.
            window_seconds: The duration of the sliding window in seconds.
                            Must be a positive integer.

        Raises:
            ValueError: If limit or window_seconds are not positive integers.
        """
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError("limit must be a positive integer")
        if not isinstance(window_seconds, int) or window_seconds <= 0:
            raise ValueError("window_seconds must be a positive integer")

        self._limit = limit
        self._window_seconds = window_seconds
        self._data: Dict[str, Deque[int]] = collections.defaultdict(collections.deque)

    def allow(self, key: str, timestamp: int) -> bool:
        """
        Determines if an event should be allowed for a given key and timestamp.

        If the number of events for the key in the half-open window
        (timestamp - window_seconds, timestamp] is less than the limit, the
        event is allowed, its timestamp is recorded, and True is returned.
        Otherwise, the event is denied, not recorded, and False is returned.

        Args:
            key: A unique identifier for the entity being rate-limited.
            timestamp: The integer timestamp of the event.

        Returns:
            bool: True if the event is allowed, False otherwise.
        """
        # Calculate the start of the window for the current timestamp.
        # Events with timestamps at or before window_start are expired.
        window_start = timestamp - self._window_seconds
        
        # Get the deque of timestamps for the given key.
        # defaultdict will create a new deque if the key is not present.
        timestamps = self._data[key]

        # Prune timestamps that are outside the current window.
        # Since timestamps are added in increasing order, we can efficiently
        # remove old ones from the left end of the deque.
        while timestamps and timestamps[0] <= window_start:
            timestamps.popleft()

        # Check if the current count is below the limit.
        if len(timestamps) < self._limit:
            # If so, record the new event timestamp and allow it.
            timestamps.append(timestamp)
            return True
        
        # Otherwise, deny the event.
        return False

    def snapshot(self, key: str) -> List[int]:
        """
        Returns a snapshot of the retained timestamps for a given key.

        Args:
            key: The identifier for the entity.

        Returns:
            A list containing the timestamps currently stored for the key.
            Returns an empty list if the key has no recorded timestamps.
        """
        # Use .get() to avoid creating a new entry in the defaultdict for a
        # key that does not exist, making this a read-only operation.
        timestamps = self._data.get(key)
        if timestamps:
            return list(timestamps)
        return []
