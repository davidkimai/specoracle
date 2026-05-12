import collections
from typing import Deque, Dict, List


class SlidingWindowLimiter:
    """
    A rate limiter using the sliding window algorithm.

    This limiter tracks event timestamps for various keys and enforces a limit
    on the number of events that can occur within a specified time window.
    The internal storage uses a deque for each key, which provides efficient
    appends and pops from both ends.
    """

    def __init__(self, limit: int, window_seconds: int):
        """
        Initializes the limiter with a rate limit and a window size.

        Args:
            limit: The maximum number of events allowed in a window.
                   Must be a positive integer.
            window_seconds: The duration of the sliding window in seconds.
                            Must be a positive integer.

        Raises:
            ValueError: If limit or window_seconds are not positive integers.
        """
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError("Limit must be a positive integer.")
        if not isinstance(window_seconds, int) or window_seconds <= 0:
            raise ValueError("Window seconds must be a positive integer.")

        self.limit = limit
        self.window_seconds = window_seconds
        self._timestamps_by_key: Dict[str, Deque[int]] = collections.defaultdict(
            collections.deque
        )

    def allow(self, key: str, timestamp: int) -> bool:
        """
        Determines if an event is allowed and records it if so.

        An event is allowed if the number of previously recorded events for the
        same key within the sliding window is less than the configured limit.
        The window is the half-open interval (timestamp - window_seconds, timestamp].

        Args:
            key: A unique identifier for the entity being rate-limited.
            timestamp: The integer timestamp of the event (e.g., Unix time).

        Returns:
            True if the event is allowed and recorded, False otherwise.
        """
        timestamps = self._timestamps_by_key[key]
        window_start_time = timestamp - self.window_seconds

        # Prune timestamps that are outside the current window.
        # Because timestamps are always added in increasing order, we can
        # efficiently remove old ones from the left of the deque.
        while timestamps and timestamps[0] <= window_start_time:
            timestamps.popleft()

        # Check if the current count is below the limit.
        if len(timestamps) < self.limit:
            timestamps.append(timestamp)
            return True

        return False

    def snapshot(self, key: str) -> List[int]:
        """
        Returns a copy of the retained timestamps for a given key.

        This method provides a view of the current state for a key without
        modifying it.

        Args:
            key: The identifier for the entity.

        Returns:
            A list of integer timestamps currently stored for the key.
            Returns an empty list if the key has no recorded events.
        """
        # Use .get() to avoid modifying the defaultdict for keys not present.
        # Return a list copy to prevent mutation of the internal deque.
        return list(self._timestamps_by_key.get(key, []))
