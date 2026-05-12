from __future__ import annotations

from datetime import timedelta
from typing import Any

__all__ = ["correlate_events"]


def _delta_seconds(later: Any, earlier: Any) -> Any:
    """Return later - earlier, expressed in seconds for datetime-like values."""
    delta = later - earlier
    if isinstance(delta, timedelta):
        return delta.total_seconds()
    return delta


def correlate_events(events: list[dict], *, within: int) -> list[tuple[dict, dict]]:
    """
    Pair each type 'A' event with the first later type 'B' event in the same
    session whose timestamp delta is between 0 and ``within`` seconds.

    Expected event keys:
      - "type": event type, where relevant values are "A" and "B"
      - "session_id": session identifier
      - "timestamp": numeric seconds or datetime/date-like value

    The returned tuples contain references to the original event dictionaries.
    """
    pairs: list[tuple[dict, dict]] = []

    for i, event in enumerate(events):
        if event.get("type") != "A":
            continue

        session_id = event["session_id"]
        start_time = event["timestamp"]

        for j in range(i + 1, len(events)):
            candidate = events[j]

            if candidate.get("type") != "B":
                continue
            if candidate.get("session_id") != session_id:
                continue

            delta = _delta_seconds(candidate["timestamp"], start_time)
            if 0 <= delta <= within:
                pairs.append((event, candidate))
                break

    return pairs
