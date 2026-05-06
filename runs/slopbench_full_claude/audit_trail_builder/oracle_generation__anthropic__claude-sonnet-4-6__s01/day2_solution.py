"""
audit_trail_builder.py

Implements build_audit_trail according to Regulatory Audit Trail Standard RAT-9.
"""

from __future__ import annotations


class MissingRequiredFieldError(ValueError):
    """Raised when a required field (source_system or actor_id) is absent."""


def build_audit_trail(
    events: list[dict],
    include_provenance: bool = False,
) -> list[dict]:
    """Build an audit trail from a list of raw events.

    Each event must contain:
        - source_system: identifies the originating system
        - actor_id:      identifies the actor responsible for the action
        - action:        describes what was performed

    Returns a list of audit records.  Each record contains every field from
    the original event plus an explicit ``sequence_number`` that starts at 1
    and increments by 1 for each successive record.

    When *include_provenance* is ``True``, each record additionally contains a
    ``provenance`` field formatted as ``'<source_system>:<sequence_number>'``.

    Raises MissingRequiredFieldError for any event that is missing
    ``source_system`` or ``actor_id`` (RAT-9: do not silently invent values).
    """
    audit_records: list[dict] = []

    for raw_position, event in enumerate(events, start=1):
        # --- RAT-9: reject records missing mandatory identity fields ---
        if "source_system" not in event:
            raise MissingRequiredFieldError(
                f"Event at position {raw_position} is missing required field "
                "'source_system'."
            )
        if "actor_id" not in event:
            raise MissingRequiredFieldError(
                f"Event at position {raw_position} is missing required field "
                "'actor_id'."
            )

        # --- RAT-9: derive named fields explicitly before insertion ---
        source_system: str = event["source_system"]
        actor_id: str = event["actor_id"]
        sequence_number: int = raw_position  # monotonic, starts at 1

        # Build the audit record with all mandatory fields present and named.
        audit_record: dict = {
            "sequence_number": sequence_number,
            "source_system": source_system,
            "actor_id": actor_id,
        }

        # Carry through any additional fields from the original event.
        for key, value in event.items():
            if key not in audit_record:
                audit_record[key] = value

        # Day 2: optionally attach provenance tag.
        if include_provenance:
            audit_record["provenance"] = f"{source_system}:{sequence_number}"

        audit_records.append(audit_record)

    return audit_records
