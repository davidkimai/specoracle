"""
A module for building a sequenced audit trail from raw events.
"""

from __future__ import annotations

import collections.abc
from typing import Any


def build_audit_trail(
    events: collections.abc.Sequence[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    Builds a sequenced audit trail from a list of raw event dictionaries.

    This function processes a list of event dictionaries. For each event, it
    validates the presence of 'source_system' and 'actor_id'. If an event is
    valid, it is copied, a sequential 'sequence_number' is added (starting
    from 1), and it's included in the returned audit trail.

    Events that fail validation by missing 'source_system' or 'actor_id' keys,
    or having falsy values for them, are silently ignored and excluded from
    the output.

    Args:
        events: A sequence of dictionaries, where each dictionary represents
                an event. An event should contain at least 'source_system'
                and 'actor_id' keys with non-falsy values.

    Returns:
        A new list of dictionaries, representing the valid audit trail
        records, each with an added 'sequence_number'. The sequence starts at 1.
    """
    audit_trail: list[dict[str, Any]] = []
    sequence_number = 1

    for event in events:
        # Reject events if required fields are missing or have falsy values
        # (e.g., None, empty string), which are treated as effectively missing.
        if not event.get("source_system") or not event.get("actor_id"):
            continue

        # Create a copy to avoid modifying the original input event data.
        record = event.copy()
        record["sequence_number"] = sequence_number
        audit_trail.append(record)
        sequence_number += 1

    return audit_trail
