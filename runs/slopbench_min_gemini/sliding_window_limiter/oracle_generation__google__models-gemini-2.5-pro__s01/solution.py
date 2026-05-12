import collections
from typing import Deque, Dict, List


class SlidingWindowLimiter:
    """
    A rate limiter using the sliding window algorithm.

    This limiter tracks event timestamps for various keys and determines whether
    a new event should be allowed based on a configurable limit within a
    time window.
    """

    def __init__(self, limit: int, window_seconds: int):
        """
        Initializes the SlidingWindowLimiter.

        Args:
            limit: The maximum number of events allowed in a window.
            window_seconds: The duration of the sliding window in seconds.

        Raises:
            ValueError: If limit or window_seconds are not positive integers.
        """
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError("limit must be a positive integer")
        if not isinstance(window_seconds, int) or window_seconds <= 0:
            raise ValueError("window_seconds must be a positive integer")

        self.limit = limit
        self.window_seconds = window_seconds
        self._timestamps: Dict[str, Deque[int]] = collections.defaultdict(collections.deque)

    def allow(self, key: str, timestamp: int) -> bool:
        """
        Determines if an event is allowed for a given key at a specific timestamp.

        If the event is allowed, its timestamp is recorded. The window is defined
        as the half-open interval (timestamp - window_seconds, timestamp].

        Args:
            key: A unique identifier for the entity being rate-limited.
            timestamp: The timestamp of the event, as an integer (e.g., Unix time).

        Returns:
            True if the event is within the rate limit, False otherwise.
        """
        self._prune_old_timestamps(key, timestamp)

        key_timestamps = self._timestamps[key]
        if len(key_timestamps) < self.limit:
            key_timestamps.append(timestamp)
            return True

        return False

    def snapshot(self, key: str) -> List[int]:
        """
        Returns a snapshot of the retained timestamps for a given key.

        Args:
            key: The key for which to retrieve the timestamps.

        Returns:
            A list of integer timestamps currently stored for the key.
        """
        return list(self._timestamps.get(key, []))

    def _prune_old_timestamps(self, key: str, current_timestamp: int) -> None:
        """
        Removes timestamps that are older than the sliding window.

        This is a helper method to keep the timestamp list for a key clean
        and relevant to the current time.

        Args:
            key: The key whose timestamps need pruning.
            current_timestamp: The current timestamp to define the window.
        """
        window_start = current_timestamp - self.window_seconds
        key_timestamps = self._timestamps[key]

        while key_timestamps and key_timestamps[0] <= window_start:
            key_timestamps.popleft()
