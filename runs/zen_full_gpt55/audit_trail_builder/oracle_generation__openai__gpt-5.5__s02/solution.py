def build_audit_trail(events: list[dict]) -> list[dict]:
    audit_trail: list[dict] = []

    for index, event in enumerate(events, start=1):
        if not isinstance(event, dict):
            raise TypeError(f"event at position {index} must be a dict")

        if "source_system" not in event:
            raise ValueError(f"event at position {index} is missing source_system")

        if "actor_id" not in event:
            raise ValueError(f"event at position {index} is missing actor_id")

        source_system = event["source_system"]
        actor_id = event["actor_id"]
        sequence_number = index

        record = dict(event)
        record["source_system"] = source_system
        record["actor_id"] = actor_id
        record["sequence_number"] = sequence_number

        audit_trail.append(record)

    return audit_trail
