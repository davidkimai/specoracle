import collections
from typing import Deque, Dict, List

class SlidingWindowLimiter:
    """
    Implements a sliding window rate limiter.

    This limiter tracks events for different keys and allows an event if the
    count of events within a specified time window is below a certain limit.
    The implementation uses a deque for each key to efficiently manage the
    timestamps within the sliding window.
    """

    def __init__(self, limit: int, window_seconds: int):
        """
        Initializes the SlidingWindowLimiter.

        Args:
            limit: The maximum number of events allowed in a window. Must be
                   a positive integer.
            window_seconds: The duration of the sliding window in seconds. Must
                            be a positive integer.

        Raises:
            ValueError: If limit or window_seconds are not positive.
        """
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError("Limit must be a positive integer.")
        if not isinstance(window_seconds, int) or window_seconds <= 0:
            raise ValueError("Window seconds must be a positive integer.")

        self._limit = limit
        self._window_seconds = window_seconds
        self._events: Dict[str, Deque[int]] = collections.defaultdict(collections.deque)

    def allow(self, key: str, timestamp: int) -> bool:
        """
        Determines if an event is allowed for a given key at a specific timestamp.

        If allowed, the event is recorded. Otherwise, it is not. The window is
        defined as the half-open interval (timestamp - window_seconds, timestamp].

        Args:
            key: A unique identifier for the entity being rate-limited.
            timestamp: The integer timestamp of the event.

        Returns:
            True if the number of events in the window is less than the limit,
            False otherwise.
        """
        timestamps = self._events[key]

        # The start of the window is exclusive. Events at or before this
        # timestamp are considered expired.
        window_start = timestamp - self._window_seconds

        # Remove all timestamps that are outside the current window.
        # Since timestamps are added in increasing order, we can efficiently
        # remove expired timestamps from the left of the deque.
        while timestamps and timestamps[0] <= window_start:
            timestamps.popleft()

        # Check if adding a new event would exceed the limit.
        if len(timestamps) < self._limit:
            # If within the limit, allow the event and record its timestamp.
            timestamps.append(timestamp)
            return True
        else:
            # Otherwise, deny the event and do not record it.
            return False

    def snapshot(self, key: str) -> List[int]:
        """
        Returns a snapshot of the retained timestamps for a given key.

        This method provides a read-only view of the current state for a key
        without modifying it.

        Args:
            key: The key for which to retrieve the timestamps.

        Returns:
            A new list containing the integer timestamps currently stored for
            the key. Returns an empty list if the key has no recorded events.
        """
        # Use .get() to avoid creating a new deque in the defaultdict
        # for a key that has not been seen before.
        timestamps = self._events.get(key)
        if timestamps:
            return list(timestamps)
        return []
