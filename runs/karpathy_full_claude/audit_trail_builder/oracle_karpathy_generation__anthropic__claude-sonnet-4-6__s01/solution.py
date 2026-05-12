"""
audit_trail_builder.py

Implements build_audit_trail per Regulatory Audit Trail Standard RAT-9.
"""

from __future__ import annotations


def build_audit_trail(events: list[dict]) -> list[dict]:
    """
    Build an ordered audit trail from a list of raw events.

    Each event must contain:
        - source_system: identifies the originating system
        - actor_id:      identifies the actor responsible for the action
        - action:        describes what was done

    Returns a list of audit records, each containing:
        - sequence_number: monotonically increasing integer starting at 1
        - source_system:   copied from the event
        - actor_id:        copied from the event
        - action:          copied from the event

    Raises:
        ValueError: if any event is missing source_system or actor_id.
    """
    audit_records: list[dict] = []

    for index, event in enumerate(events):
        # RAT-9: reject records missing source_system or actor_id
        if "source_system" not in event or event["source_system"] is None:
            raise ValueError(
                f"Event at position {index} is missing required field 'source_system'."
            )
        if "actor_id" not in event or event["actor_id"] is None:
            raise ValueError(
                f"Event at position {index} is missing required field 'actor_id'."
            )

        # RAT-9: derive named fields explicitly before inserting into record
        sequence_number: int = index + 1
        source_system: str = event["source_system"]
        actor_id: str = event["actor_id"]
        action = event.get("action")

        audit_record: dict = {
            "sequence_number": sequence_number,
            "source_system": source_system,
            "actor_id": actor_id,
            "action": action,
        }

        audit_records.append(audit_record)

    return audit_records
