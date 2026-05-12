"""Audit trail builder module."""

_REQUIRED_FIELDS = ("source_system", "actor_id")


def build_audit_trail(events: list[dict]) -> list[dict]:
    """
    Build audit records from event dictionaries.

    Each returned record contains the event fields plus a monotonic
    ``sequence_number`` starting at 1.

    Raises:
        TypeError: If ``events`` is not a list or an event is not a dict.
        ValueError: If an event is missing ``source_system`` or ``actor_id``,
            or either value is None.
    """
    if not isinstance(events, list):
        raise TypeError("events must be a list of dictionaries")

    audit_trail: list[dict] = []

    for index, event in enumerate(events):
        if not isinstance(event, dict):
            raise TypeError(f"event at index {index} must be a dictionary")

        for field_name in _REQUIRED_FIELDS:
            if field_name not in event:
                raise ValueError(f"event at index {index} is missing {field_name}")
            if event[field_name] is None:
                raise ValueError(f"event at index {index} has null {field_name}")

        sequence_number = index + 1
        source_system = event["source_system"]
        actor_id = event["actor_id"]

        audit_record = dict(event)
        audit_record["sequence_number"] = sequence_number
        audit_record["source_system"] = source_system
        audit_record["actor_id"] = actor_id

        audit_trail.append(audit_record)

    return audit_trail
