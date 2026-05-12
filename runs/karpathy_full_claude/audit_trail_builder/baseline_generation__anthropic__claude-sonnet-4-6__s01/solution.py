"""
audit_trail_builder.py

Provides build_audit_trail for constructing a sequenced, validated audit trail
from a list of raw event dictionaries.
"""

from __future__ import annotations


def build_audit_trail(events: list[dict]) -> list[dict]:
    """Build a sequenced audit trail from a list of event dictionaries.

    Each event must contain at minimum:
        - source_system (str): The originating system.
        - actor_id (str | int): The identifier of the actor performing the action.

    Optional fields (e.g. ``action``) are preserved as-is.

    Args:
        events: A list of raw event dictionaries.

    Returns:
        A list of audit record dictionaries, each enriched with a ``sequence``
        field starting at 1, in the same order as the accepted input events.

    Raises:
        ValueError: If any event is missing ``source_system`` or ``actor_id``.
        TypeError: If ``events`` is not a list.
    """
    if not isinstance(events, list):
        raise TypeError(
            f"events must be a list, got {type(events).__name__!r}"
        )

    audit_trail: list[dict] = []
    sequence = 1

    for index, event in enumerate(events):
        if not isinstance(event, dict):
            raise TypeError(
                f"Event at index {index} must be a dict, got {type(event).__name__!r}"
            )

        missing_fields = [
            field for field in ("source_system", "actor_id")
            if field not in event
        ]
        if missing_fields:
            raise ValueError(
                f"Event at index {index} is missing required field(s): "
                f"{', '.join(missing_fields)!r}. Event: {event!r}"
            )

        record = {
            "sequence": sequence,
            **event,
        }
        audit_trail.append(record)
        sequence += 1

    return audit_trail
