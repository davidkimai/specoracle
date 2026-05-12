from typing import Any


def build_audit_trail(events: list[dict]) -> list[dict]:
    """
    Build an audit trail from event dictionaries.

    Each returned audit record is a shallow copy of the input event with an
    added ``sequence_number`` field. Sequence numbers start at 1 and follow the
    input order.

    Events missing ``source_system`` or ``actor_id`` are rejected.

    Args:
        events: A list of event dictionaries.

    Returns:
        A list of audit trail record dictionaries.

    Raises:
        TypeError: If events is not a list or any event is not a dictionary.
        ValueError: If an event is missing source_system or actor_id.
    """
    if not isinstance(events, list):
        raise TypeError("events must be a list of dictionaries")

    audit_trail: list[dict[str, Any]] = []

    for index, event in enumerate(events, start=1):
        if not isinstance(event, dict):
            raise TypeError(f"event at index {index - 1} must be a dictionary")

        if "source_system" not in event:
            raise ValueError(f"event at index {index - 1} is missing source_system")

        if "actor_id" not in event:
            raise ValueError(f"event at index {index - 1} is missing actor_id")

        record = dict(event)
        record["sequence_number"] = index
        audit_trail.append(record)

    return audit_trail
