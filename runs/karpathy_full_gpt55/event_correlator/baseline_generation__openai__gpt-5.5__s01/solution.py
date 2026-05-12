__all__ = ["correlate_events"]


def _is_later(
    later_time: object,
    later_index: int,
    earlier_time: object,
    earlier_index: int,
) -> bool:
    if later_time > earlier_time:
        return True
    return later_time == earlier_time and later_index > earlier_index


def _seconds_between(later_time: object, earlier_time: object) -> object:
    delta = later_time - earlier_time
    total_seconds = getattr(delta, "total_seconds", None)
    if callable(total_seconds):
        return total_seconds()
    return delta


def _precedes(
    candidate_time: object,
    candidate_index: int,
    current_time: object,
    current_index: int,
) -> bool:
    if candidate_time < current_time:
        return True
    return candidate_time == current_time and candidate_index < current_index


def correlate_events(events: list[dict], *, within: int) -> list[tuple[dict, dict]]:
    pairs: list[tuple[dict, dict]] = []
    indexed_events = list(enumerate(events))

    for a_index, a_event in indexed_events:
        if a_event.get("type") != "A":
            continue
        if "session_id" not in a_event or "timestamp" not in a_event:
            continue

        session_id = a_event["session_id"]
        a_time = a_event["timestamp"]

        best_b_event: dict | None = None
        best_b_time: object | None = None
        best_b_index: int | None = None

        for b_index, b_event in indexed_events:
            if b_event.get("type") != "B":
                continue
            if "session_id" not in b_event or "timestamp" not in b_event:
                continue
            if b_event["session_id"] != session_id:
                continue

            b_time = b_event["timestamp"]
            if not _is_later(b_time, b_index, a_time, a_index):
                continue

            delta_seconds = _seconds_between(b_time, a_time)
            if delta_seconds < 0 or delta_seconds > within:
                continue

            if (
                best_b_event is None
                or _precedes(b_time, b_index, best_b_time, best_b_index)  # type: ignore[arg-type]
            ):
                best_b_event = b_event
                best_b_time = b_time
                best_b_index = b_index

        if best_b_event is not None:
            pairs.append((a_event, best_b_event))

    return pairs
