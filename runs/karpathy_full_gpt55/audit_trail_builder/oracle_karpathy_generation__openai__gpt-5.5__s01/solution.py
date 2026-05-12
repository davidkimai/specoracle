from typing import Any

SOURCE_SYSTEM_FIELD = "source_system"
ACTOR_ID_FIELD = "actor_id"
ACTION_FIELD = "action"
SEQUENCE_NUMBER_FIELD = "sequence_number"

REQUIRED_FIELDS = (SOURCE_SYSTEM_FIELD, ACTOR_ID_FIELD, ACTION_FIELD)


def build_audit_trail(events: list[dict]) -> list[dict]:
    """
    Build audit records from event dictionaries.

    Each returned record is a shallow copy of the corresponding input event with
    a monotonic sequence_number added, starting at 1.

    Raises:
        TypeError: If events is not a list or an event is not a dict.
        ValueError: If an event is missing source_system, actor_id, or action,
            or if source_system/actor_id is None.
    """
    if not isinstance(events, list):
        raise TypeError("events must be a list of dictionaries")

    audit_records: list[dict[str, Any]] = []

    for event_index, event in enumerate(events):
        if not isinstance(event, dict):
            raise TypeError(f"event at index {event_index} must be a dictionary")

        for field_name in REQUIRED_FIELDS:
            if field_name not in event:
                raise ValueError(f"event at index {event_index} is missing {field_name!r}")

        source_system = event[SOURCE_SYSTEM_FIELD]
        actor_id = event[ACTOR_ID_FIELD]

        if source_system is None:
            raise ValueError(f"event at index {event_index} has no source_system")
        if actor_id is None:
            raise ValueError(f"event at index {event_index} has no actor_id")

        sequence_number = event_index + 1

        audit_record = dict(event)
        audit_record[SOURCE_SYSTEM_FIELD] = source_system
        audit_record[ACTOR_ID_FIELD] = actor_id
        audit_record[SEQUENCE_NUMBER_FIELD] = sequence_number

        audit_records.append(audit_record)

    return audit_records
