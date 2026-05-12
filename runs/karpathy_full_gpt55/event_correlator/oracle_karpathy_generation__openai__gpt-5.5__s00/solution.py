from __future__ import annotations


def correlate_events(events: list[dict], *, within: int) -> list[tuple[dict, dict]]:
    """
    Pair each type 'A' event with the first later type 'B' event in the same
    session_id whose timestamp delta is no more than within seconds.

    Expected event keys: 'type', 'session_id', 'timestamp'.
    Events missing these keys are ignored.
    """
    if within < 0:
        return []

    indexed_events = []
    for index, event in enumerate(events):
        try:
            event_type = event["type"]
            session_id = event["session_id"]
            timestamp = event["timestamp"]
        except KeyError:
            continue
        if event_type in ("A", "B"):
            indexed_events.append((session_id, timestamp, index, event_type, event))

    indexed_events.sort(key=lambda item: (item[0], item[1], item[2]))

    pairs: list[tuple[dict, dict]] = []
    pending_a: list[tuple[object, int, dict]] = []
    current_session = object()

    for session_id, timestamp, index, event_type, event in indexed_events:
        if session_id != current_session:
            current_session = session_id
            pending_a = []

        if event_type == "A":
            pending_a.append((timestamp, index, event))
            continue

        remaining: list[tuple[object, int, dict]] = []
        for a_timestamp, a_index, a_event in pending_a:
            delta = timestamp - a_timestamp
            if delta <= 0:
                remaining.append((a_timestamp, a_index, a_event))
            elif delta <= within:
                pairs.append((a_event, event))
            else:
                remaining.append((a_timestamp, a_index, a_event))
        pending_a = remaining

    return pairs
