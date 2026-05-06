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
        A new list of records, one per accepted event, augmented with a
        ``sequence`` field that starts at 1 and increments by 1 for every
        accepted record.  Events that are missing ``source_system`` or
        ``actor_id`` are silently rejected (not included in the output).

    Notes
    -----
    * The original event dictionaries are never mutated.
    * The ``sequence`` counter only advances for *accepted* events.
    """
    if not isinstance(events, list):
        raise TypeError(f"events must be a list, got {type(events).__name__!r}")

    audit_trail: list[dict] = []
    sequence = 1

    for index, event in enumerate(events):
        if not isinstance(event, dict):
            raise TypeError(
                f"Each event must be a dict; item at index {index} is "
                f"{type(event).__name__!r}"
            )

        # Reject if required fields are absent or their values are None /
        # empty string (treat those the same as missing).
        source_system = event.get("source_system")
        actor_id = event.get("actor_id")

        if not source_system and source_system != 0:
            continue
        if not actor_id and actor_id != 0:
            continue

        record = {
            "sequence": sequence,
            "source_system": source_system,
            "actor_id": actor_id,
            "action": event.get("action"),
        }

        # Carry over any additional fields from the original event so that
        # no information is silently dropped.
        for key, value in event.items():
            if key not in record:
                record[key] = value

        audit_trail.append(record)
        sequence += 1

    return audit_trail
