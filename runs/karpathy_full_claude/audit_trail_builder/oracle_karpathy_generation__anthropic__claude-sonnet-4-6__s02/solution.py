"""
audit_trail_builder.py

Implements build_audit_trail according to Regulatory Audit Trail Standard RAT-9.
"""

from __future__ import annotations


class MissingRequiredFieldError(ValueError):
    """Raised when an event is missing source_system or actor_id."""


def build_audit_trail(events: list[dict]) -> list[dict]:
    """
    Build an audit trail from a list of events.

    Each event must contain:
        - source_system (str): The originating system.
        - actor_id (str): The actor performing the action.
        - action (str): The action performed.

    Returns a list of audit records, each containing:
        - sequence_number (int): Monotonically increasing, starting at 1.
        - source_system (str): Copied from the event.
        - actor_id (str): Copied from the event.
        - action (str): Copied from the event.

    Raises MissingRequiredFieldError if any event is missing source_system
    or actor_id.
    """
    audit_records: list[dict] = []

    for index, event in enumerate(events):
        # RAT-9: Do not silently invent actor or source values;
        # reject records missing either field.
        if "source_system" not in event or event["source_system"] is None:
            raise MissingRequiredFieldError(
                f"Event at index {index} is missing required field 'source_system'."
            )
        if "actor_id" not in event or event["actor_id"] is None:
            raise MissingRequiredFieldError(
                f"Event at index {index} is missing required field 'actor_id'."
            )

        # RAT-9: Derived fields must be named explicitly before being inserted.
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
