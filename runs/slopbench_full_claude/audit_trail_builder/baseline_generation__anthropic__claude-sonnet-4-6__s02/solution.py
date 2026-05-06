"""
audit_trail_builder.py

Provides build_audit_trail for constructing a sequenced, validated audit trail
from a list of raw event dictionaries.
"""

from __future__ import annotations


def build_audit_trail(events: list[dict]) -> list[dict]:
    """
    Build a sequenced audit trail from a list of event dictionaries.

    Each event must contain at minimum:
        - source_system (str): the originating system
        - actor_id      (str): the identifier of the actor performing the action

    An optional 'action' field is carried through if present.

    Parameters
    ----------
    events : list[dict]
        Raw event records to process.

    Returns
    -------
    list[dict]
        Validated event records with an added 'sequence' field starting at 1.

    Raises
    ------
    TypeError
        If *events* is not a list.
    ValueError
        If any event is missing the required 'source_system' or 'actor_id' fields,
        or if an event is not a dictionary.
    """
    if not isinstance(events, list):
        raise TypeError(
            f"events must be a list, got {type(events).__name__!r}"
        )

    required_fields = ("source_system", "actor_id")
    audit_trail: list[dict] = []

    for index, event in enumerate(events):
        if not isinstance(event, dict):
            raise ValueError(
                f"Event at position {index} is not a dict: {event!r}"
            )

        missing = [field for field in required_fields if field not in event]
        if missing:
            raise ValueError(
                f"Event at position {index} is missing required field(s): "
                f"{', '.join(missing)!r}. Event: {event!r}"
            )

        # Validate that required fields are not None
        for field in required_fields:
            if event[field] is None:
                raise ValueError(
                    f"Event at position {index} has None value for required "
                    f"field {field!r}. Event: {event!r}"
                )

        record = {
            "sequence": index + 1,
            "source_system": event["source_system"],
            "actor_id": event["actor_id"],
        }

        # Carry through 'action' if present
        if "action" in event:
            record["action"] = event["action"]

        # Carry through any additional fields that are not already set
        for key, value in event.items():
            if key not in record:
                record[key] = value

        audit_trail.append(record)

    return audit_trail
