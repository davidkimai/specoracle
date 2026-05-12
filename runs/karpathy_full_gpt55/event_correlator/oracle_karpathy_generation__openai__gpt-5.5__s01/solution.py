def correlate_events(events: list[dict], *, within: int) -> list[tuple[dict, dict]]:
    pairs = []

    for i, event in enumerate(events):
        if event.get("type") != "A":
            continue

        session_id = event.get("session_id")
        timestamp = event["timestamp"]

        for candidate in events[i + 1:]:
            if candidate.get("type") != "B":
                continue
            if candidate.get("session_id") != session_id:
                continue

            delta = candidate["timestamp"] - timestamp
            if 0 <= delta <= within:
                pairs.append((event, candidate))
                break

    return pairs
