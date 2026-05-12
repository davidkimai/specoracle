def build_audit_trail(events: list[dict]) -> list[dict]:
    """
    Build an audit trail from event dictionaries.

    Each output record contains:
    - sequence_number: a monotonic number starting at 1
    - source_system: copied from the event
    - actor_id: copied from the event
    - action: copied from the event

    Events missing source_system or actor_id are rejected.
    """
    if not isinstance(events, list):
        raise TypeError("events must be a list of dictionaries")

    audit_trail: list[dict] = []

    for index, event in enumerate(events, start=1):
        if not isinstance(event, dict):
            raise TypeError("each event must be a dictionary")

        if "source_system" not in event or event["source_system"] is None:
            raise ValueError("event is missing source_system")

        if "actor_id" not in event or event["actor_id"] is None:
            raise ValueError("event is missing actor_id")

        if "action" not in event:
            raise ValueError("event is missing action")

        sequence_number = index
        source_system = event["source_system"]
        actor_id = event["actor_id"]
        action = event["action"]

        record = {
            "sequence_number": sequence_number,
            "source_system": source_system,
            "actor_id": actor_id,
            "action": action,
        }

        audit_trail.append(record)

    return audit_trail
