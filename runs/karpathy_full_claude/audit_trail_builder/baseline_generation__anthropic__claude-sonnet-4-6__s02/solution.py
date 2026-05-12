"""
audit_trail_builder.py

Provides build_audit_trail for constructing a sequenced, validated audit trail
from a list of raw event dictionaries.
"""

from __future__ import annotations


def build_audit_trail(events: list[dict]) -> list[dict]:
    """Build a validated, sequenced audit trail from raw events.

    Parameters
    ----------
    events:
        A list of event dictionaries.  Each event is expected to contain at
        least the keys ``source_system``, ``actor_id``, and ``action``.

    Returns
    -------
    list[dict]
        A new list of record dictionaries.  Each record preserves all fields
        from the original event and adds a ``sequence`` key starting at 1.
        Events that are missing ``source_system`` or ``actor_id`` are silently
        rejected (not included in the output).

    Raises
    ------
    TypeError
        If *events* is not a list, or if any element is not a dict.
    """
    if not isinstance(events, list):
        raise TypeError(f"events must be a list, got {type(events).__name__!r}")

    trail: list[dict] = []
    sequence = 1

    for index, event in enumerate(events):
        if not isinstance(event, dict):
            raise TypeError(
                f"Each event must be a dict; element at index {index} is "
                f"{type(event).__name__!r}"
            )

        # Reject events that are missing required fields or whose required
        # field values are None / empty string.
        source_system = event.get("source_system")
        actor_id = event.get("actor_id")

        if not source_system and source_system != 0:
            # source_system is missing, None, or empty – reject.
            continue
        if not actor_id and actor_id != 0:
            # actor_id is missing, None, or empty – reject.
            continue

        record = {"sequence": sequence}
        record.update(event)
        trail.append(record)
        sequence += 1

    return trail
