"""
audit_trail_builder.py

Provides build_audit_trail for constructing a sequenced, validated audit trail
from a list of raw event dictionaries.
"""

from __future__ import annotations


def build_audit_trail(events: list[dict]) -> list[dict]:
    """Build a sequenced audit trail from a list of event dictionaries.

    Each event must contain at minimum:
        - source_system (str): The originating system identifier.
        - actor_id      (str): The identifier of the actor performing the action.

    Optional but recognised field:
        - action        (any): Description of the action taken.

    Returns a new list of records, each containing all original fields plus a
    ``sequence`` number starting at 1 for the first accepted event.

    Raises
    ------
    ValueError
        If any event is missing ``source_system`` or ``actor_id``.
    TypeError
        If *events* is not a list, or if any element is not a dict.
    """
    if not isinstance(events, list):
        raise TypeError(
            f"events must be a list, got {type(events).__name__!r}"
        )

    trail: list[dict] = []
    sequence = 1

    for index, event in enumerate(events):
        if not isinstance(event, dict):
            raise TypeError(
                f"Each event must be a dict; element at index {index} is "
                f"{type(event).__name__!r}"
            )

        missing_fields = [
            field for field in ("source_system", "actor_id")
            if field not in event
        ]
        if missing_fields:
            raise ValueError(
                f"Event at index {index} is missing required field(s): "
                f"{missing_fields!r}. Event contents: {event!r}"
            )

        # Validate that required fields are not None
        for field in ("source_system", "actor_id"):
            if event[field] is None:
                raise ValueError(
                    f"Event at index {index} has None value for required "
                    f"field {field!r}. Event contents: {event!r}"
                )

        record = dict(event)           # shallow copy to avoid mutating input
        record["sequence"] = sequence
        trail.append(record)
        sequence += 1

    return trail
