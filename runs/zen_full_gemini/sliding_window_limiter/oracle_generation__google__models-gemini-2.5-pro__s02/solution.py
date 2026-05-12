import collections
from typing import Deque, Dict, List


class SlidingWindowLimiter:
    """
    A rate limiter using the sliding window algorithm.

    This limiter tracks event timestamps for different keys and allows an event
    only if the count of events within a specified time window is below a limit.
    """

    _limit: int
    _window_seconds: int
    _timestamps: Dict[str, Deque[int]]

    def __init__(self, limit: int, window_seconds: int):
        """
        Initializes the SlidingWindowLimiter.

        Args:
            limit: The maximum number of events allowed in the window. Must be
                   a positive integer.
            window_seconds: The duration of the sliding window in seconds. Must
                            be a positive integer.

        Raises:
            ValueError: If limit or window_seconds are not positive integers.
        """
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError("limit must be a positive integer")
        if not isinstance(window_seconds, int) or window_seconds <= 0:
            raise ValueError("window_seconds must be a positive integer")

        self._limit = limit
        self._window_seconds = window_seconds
        self._timestamps = collections.defaultdict(collections.deque)

    def _prune_old_timestamps(self, key_timestamps: Deque[int], timestamp: int):
        """
        Removes timestamps that are outside the current window.

        The window is defined as (timestamp - window_seconds, timestamp].
        This method modifies the deque in place for efficiency.
        """
        window_start = timestamp - self._window_seconds
        while key_timestamps and key_timestamps[0] <= window_start:
            key_timestamps.popleft()

    def allow(self, key: str, timestamp: int) -> bool:
        """
        Determines if an event should be allowed for a given key.

        If the event is allowed, its timestamp is recorded. The check is
        performed against events in the half-open window
        (timestamp - window_seconds, timestamp].

        Args:
            key: A unique identifier for the entity being rate-limited.
            timestamp: The integer timestamp of the event.

        Returns:
            True if the event is within the limit, False otherwise.
        """
        key_timestamps = self._timestamps[key]
        self._prune_old_timestamps(key_timestamps, timestamp)

        if len(key_timestamps) < self._limit:
            key_timestamps.append(timestamp)
            return True

        return False

    def snapshot(self, key: str) -> List[int]:
        """
        Returns a snapshot of the retained timestamps for a given key.

        Args:
            key: The key for which to retrieve timestamps.

        Returns:
            A list of integer timestamps currently stored for the key.
            Returns an empty list if the key is not tracked.
        """
        # Use .get() to avoid creating a new deque for a non-existent key,
        # which would be a side-effect of using self._timestamps[key].
        return list(self._timestamps.get(key, []))
