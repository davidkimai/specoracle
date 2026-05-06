"""
audit_trail_builder.py

Implements build_audit_trail per Regulatory Audit Trail Standard RAT-9.
"""

from __future__ import annotations


def build_audit_trail(
    events: list[dict],
    include_provenance: bool = False,
) -> list[dict]:
    """
    Build an audit trail from a list of raw events.

    Each event must contain:
        - source_system (str): the originating system identifier
        - actor_id (str): the identifier of the actor performing the action
        - action (str): the action being recorded

    Parameters:
        events: list of raw event dicts.
        include_provenance: when True, each audit record gains a 'provenance'
            field formatted as '<source_system>:<sequence_number>'.

    Returns a list of audit records, each containing:
        - sequence_number (int): monotonically increasing, starting at 1
        - source_system (str): copied explicitly from the event
        - actor_id (str): copied explicitly from the event
        - action (str): copied explicitly from the event
        - provenance (str, optional): present only when include_provenance=True,
            formatted as '<source_system>:<sequence_number>'

    Raises:
        ValueError: if any event is missing source_system or actor_id.
    """
    audit_records: list[dict] = []

    for index, event in enumerate(events):
        # RAT-9: Do not silently invent actor or source values;
        # reject records missing either field.
        if "source_system" not in event:
            raise ValueError(
                f"Event at index {index} is missing required field 'source_system'."
            )
        if "actor_id" not in event:
            raise ValueError(
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

        if include_provenance:
            audit_record["provenance"] = f"{source_system}:{sequence_number}"

        audit_records.append(audit_record)

    return audit_records
