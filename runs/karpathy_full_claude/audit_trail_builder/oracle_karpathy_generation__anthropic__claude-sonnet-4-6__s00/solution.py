"""
audit_trail_builder.py

Implements build_audit_trail per Regulatory Audit Trail Standard RAT-9.

Every audit record carries:
  - source_system  (must be present in the incoming event)
  - actor_id       (must be present in the incoming event)
  - sequence_number (monotonic, starting at 1)
  - action         (copied from the incoming event)

Records missing source_system or actor_id are rejected with a ValueError.
Derived fields are named explicitly before insertion.
"""

from __future__ import annotations


def build_audit_trail(events: list[dict]) -> list[dict]:
    """Build a sequence-numbered audit trail from a list of raw events.

    Parameters
    ----------
    events:
        A list of dicts, each expected to contain at minimum the keys
        ``source_system``, ``actor_id``, and ``action``.

    Returns
    -------
    list[dict]
        Ordered audit records, each containing ``sequence_number``,
        ``source_system``, ``actor_id``, and ``action``.

    Raises
    ------
    ValueError
        If any event is missing ``source_system`` or ``actor_id``.
    TypeError
        If *events* is not a list, or any element is not a dict.
    """
    if not isinstance(events, list):
        raise TypeError(
            f"events must be a list, got {type(events).__name__!r}"
        )

    audit_records: list[dict] = []

    for index, event in enumerate(events):
        if not isinstance(event, dict):
            raise TypeError(
                f"Each event must be a dict; event at index {index} is "
                f"{type(event).__name__!r}"
            )

        # RAT-9: Do not silently invent actor or source values;
        # reject records missing either field.
        if "source_system" not in event:
            raise ValueError(
                f"Event at index {index} is missing required field "
                f"'source_system'."
            )
        if "actor_id" not in event:
            raise ValueError(
                f"Event at index {index} is missing required field "
                f"'actor_id'."
            )

        # RAT-9: Derived fields must be named explicitly before being
        # inserted into a record.
        sequence_number: int = index + 1
        source_system: str = event["source_system"]
        actor_id = event["actor_id"]
        action = event.get("action")

        audit_record: dict = {
            "sequence_number": sequence_number,
            "source_system": source_system,
            "actor_id": actor_id,
            "action": action,
        }

        audit_records.append(audit_record)

    return audit_records
