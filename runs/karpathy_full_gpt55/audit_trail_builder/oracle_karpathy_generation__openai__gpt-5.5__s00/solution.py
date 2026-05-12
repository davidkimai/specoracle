from typing import Any


def build_audit_trail(events: list[dict]) -> list[dict]:
    audit_records: list[dict] = []

    for event_index, event in enumerate(events):
        if not isinstance(event, dict):
            raise TypeError(f"event at index {event_index} must be a dict")

        if "source_system" not in event or event["source_system"] is None:
            raise ValueError(f"event at index {event_index} is missing source_system")

        if "actor_id" not in event or event["actor_id"] is None:
            raise ValueError(f"event at index {event_index} is missing actor_id")

        source_system: Any = event["source_system"]
        actor_id: Any = event["actor_id"]
        action: Any = event.get("action")
        sequence_number: int = event_index + 1

        audit_record: dict = {
            "source_system": source_system,
            "actor_id": actor_id,
            "action": action,
            "sequence_number": sequence_number,
        }

        audit_records.append(audit_record)

    return audit_records
