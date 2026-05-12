def build_audit_trail(events: list[dict]) -> list[dict]:
    """
    Build an audit trail from event dictionaries.

    Each returned record is a shallow copy of the input event with an added
    ``sequence_number`` field. Sequence numbers start at 1 and follow the input
    order.

    Events missing ``source_system`` or ``actor_id`` are rejected by raising
    ValueError.
    """
    if not isinstance(events, list):
        raise TypeError("events must be a list of dictionaries")

    audit_trail: list[dict] = []

    for index, event in enumerate(events, start=1):
        if not isinstance(event, dict):
            raise TypeError(f"event at position {index} must be a dictionary")

        missing_fields = [
            field for field in ("source_system", "actor_id") if field not in event
        ]
        if missing_fields:
            fields = ", ".join(missing_fields)
            raise ValueError(f"event at position {index} is missing required field(s): {fields}")

        record = dict(event)
        record["sequence_number"] = index
        audit_trail.append(record)

    return audit_trail
