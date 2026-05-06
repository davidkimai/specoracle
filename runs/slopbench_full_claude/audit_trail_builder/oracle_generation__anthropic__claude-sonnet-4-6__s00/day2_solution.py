"""
audit_trail_builder.py

Implements build_audit_trail according to Regulatory Audit Trail Standard RAT-9.
"""

from __future__ import annotations


class MissingRequiredFieldError(ValueError):
    """Raised when an event is missing source_system or actor_id."""


def build_audit_trail(
    events: list[dict],
    include_provenance: bool = False,
) -> list[dict]:
    """
    Build an ordered audit trail from a list of events.

    Each event must contain:
        - source_system (str): the originating system identifier
        - actor_id (str): the identifier of the actor performing the action
        - action (str): the action being recorded

    Parameters:
        events: list of event dicts to process.
        include_provenance: when True, each audit record gains a
            ``provenance`` field formatted as '<source_system>:<sequence_number>'.

    Returns a list of audit records, each containing:
        - sequence_number (int): monotonically increasing, starting at 1
        - source_system (str): copied from the event
        - actor_id (str): copied from the event
        - action (str): copied from the event
        - provenance (str, optional): present only when include_provenance is True

    Raises:
        MissingRequiredFieldError: if any event is missing source_system or actor_id.
        TypeError: if events is not a list or any element is not a dict.
    """
    if not isinstance(events, list):
        raise TypeError(f"events must be a list, got {type(events).__name__!r}")

    audit_records: list[dict] = []

    for index, event in enumerate(events):
        if not isinstance(event, dict):
            raise TypeError(
                f"Each event must be a dict; event at index {index} is "
                f"{type(event).__name__!r}"
            )

        # RAT-9: reject records missing source_system or actor_id
        if "source_system" not in event or event["source_system"] is None:
            raise MissingRequiredFieldError(
                f"Event at index {index} is missing required field 'source_system'."
            )
        if "actor_id" not in event or event["actor_id"] is None:
            raise MissingRequiredFieldError(
                f"Event at index {index} is missing required field 'actor_id'."
            )

        # RAT-9: derive named fields explicitly before inserting into a record
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
