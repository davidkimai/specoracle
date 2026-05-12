def _delta_seconds(later, earlier):
    delta = later - earlier
    if hasattr(delta, "total_seconds"):
        return delta.total_seconds()
    return delta


def correlate_events(events: list[dict], *, within: int) -> list[tuple[dict, dict]]:
    pairs = []

    for index, event in enumerate(events):
        if event.get("type") != "A":
            continue

        session_id = event["session_id"]
        event_time = event["timestamp"]

        for later_event in events[index + 1:]:
            if later_event.get("type") != "B":
                continue
            if later_event["session_id"] != session_id:
                continue

            delta = _delta_seconds(later_event["timestamp"], event_time)
            if 0 <= delta <= within:
                pairs.append((event, later_event))
                break

    return pairs
