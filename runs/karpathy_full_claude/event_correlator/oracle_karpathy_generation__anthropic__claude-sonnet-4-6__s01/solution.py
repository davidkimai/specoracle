from collections import defaultdict


def correlate_events(events: list[dict], *, within: int) -> list[tuple[dict, dict]]:
    # Group events by session_id
    sessions = defaultdict(list)
    for event in events:
        sessions[event["session_id"]].append(event)

    # Sort each session's events by timestamp
    for session_id in sessions:
        sessions[session_id].sort(key=lambda e: e["timestamp"])

    pairs = []

    for session_events in sessions.values():
        # For each A event, find the first B event after it within `within` seconds
        b_start = 0  # optimization: track minimum B index to consider
        a_indices = [i for i, e in enumerate(session_events) if e["type"] == "A"]
        b_indices = [i for i, e in enumerate(session_events) if e["type"] == "B"]

        for a_idx in a_indices:
            a_event = session_events[a_idx]
            for b_idx in b_indices:
                b_event = session_events[b_idx]
                if b_event["timestamp"] <= a_event["timestamp"]:
                    continue
                delta = b_event["timestamp"] - a_event["timestamp"]
                if delta <= within:
                    pairs.append((a_event, b_event))
                    break
                else:
                    # B events are sorted; if this one is already too far, stop
                    break

    return pairs
