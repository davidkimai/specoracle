from collections import defaultdict


def correlate_events(events: list[dict], *, within: int) -> list[tuple[dict, dict]]:
    """
    Pair each type 'A' event with the first later type 'B' event in the same
    session_id where the time delta is no more than `within` seconds.

    Assumptions:
    - Each event dict has keys: 'session_id', 'type', 'timestamp' (numeric seconds).
    - An 'A' event is paired with the first 'B' event that occurs strictly later
      (timestamp_B > timestamp_A) within the same session, with
      (timestamp_B - timestamp_A) <= within.
    - Each 'A' event is paired at most once; each 'B' event may only be used once
      (consumed by the first eligible 'A' that claims it).
    - Events are not assumed to be pre-sorted.
    """
    by_session = defaultdict(list)
    for event in events:
        by_session[event['session_id']].append(event)

    pairs = []

    for session_events in by_session.values():
        sorted_events = sorted(session_events, key=lambda e: e['timestamp'])

        a_events = [e for e in sorted_events if e['type'] == 'A']
        b_events = [e for e in sorted_events if e['type'] == 'B']

        used_b = set()

        for a in a_events:
            for i, b in enumerate(b_events):
                if i in used_b:
                    continue
                if b['timestamp'] <= a['timestamp']:
                    continue
                if b['timestamp'] - a['timestamp'] <= within:
                    pairs.append((a, b))
                    used_b.add(i)
                    break

    return pairs
