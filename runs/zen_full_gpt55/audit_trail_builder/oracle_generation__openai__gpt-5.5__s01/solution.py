_SEQUENCE_FIELD = "sequence_number"
_SOURCE_FIELD = "source_system"
_ACTOR_FIELD = "actor_id"
_ACTION_FIELD = "action"


def build_audit_trail(events: list[dict]) -> list[dict]:
    """Build audit records from events, assigning monotonic sequence numbers."""
    if not isinstance(events, list):
        raise TypeError("events must be a list of dictionaries")

    audit_trail: list[dict] = []

    for index, event in enumerate(events):
        if not isinstance(event, dict):
            raise TypeError(f"event at index {index} must be a dictionary")

        if _SOURCE_FIELD not in event:
            raise ValueError(f"event at index {index} is missing source_system")
        if _ACTOR_FIELD not in event:
            raise ValueError(f"event at index {index} is missing actor_id")
        if _ACTION_FIELD not in event:
            raise ValueError(f"event at index {index} is missing action")

        source_system = event[_SOURCE_FIELD]
        actor_id = event[_ACTOR_FIELD]
        action = event[_ACTION_FIELD]
        sequence_number = index + 1

        if source_system is None:
            raise ValueError(f"event at index {index} has no source_system")
        if actor_id is None:
            raise ValueError(f"event at index {index} has no actor_id")

        record = dict(event)
        record[_SOURCE_FIELD] = source_system
        record[_ACTOR_FIELD] = actor_id
        record[_ACTION_FIELD] = action
        record[_SEQUENCE_FIELD] = sequence_number

        audit_trail.append(record)

    return audit_trail
