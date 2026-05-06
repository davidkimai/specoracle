"""
audit_trail_builder.py

Builds an audit trail from a list of raw event dictionaries.
"""


def build_audit_trail(events: list[dict], include_provenance: bool = False) -> list[dict]:
    """
    Build an audit trail from a list of events.

    Each event must contain at least:
        - source_system (str): The originating system.
        - actor_id (str): The identifier of the actor performing the action.
        - action (str): The action performed (optional but typically present).

    Events missing 'source_system' or 'actor_id' are rejected (skipped).

    Returns a list of audit records with an added 'sequence' field starting at 1,
    preserving the order of valid events.

    When include_provenance is True, each record also contains a 'provenance'
    field formatted as '<source_system>:<sequence>'.

    Parameters
    ----------
    events : list[dict]
        Raw event dictionaries to process.
    include_provenance : bool, optional
        When True, add a 'provenance' field to each record. Defaults to False.

    Returns
    -------
    list[dict]
        Ordered audit records with sequence numbers.

    Raises
    ------
    TypeError
        If `events` is not a list.
    """
    if not isinstance(events, list):
        raise TypeError(f"Expected a list of events, got {type(events).__name__!r}.")

    audit_trail: list[dict] = []
    sequence = 1

    for index, event in enumerate(events):
        if not isinstance(event, dict):
            # Non-dict entries are silently skipped to be permissive about
            # heterogeneous input while still protecting downstream consumers.
            continue

        missing_fields = [
            field for field in ("source_system", "actor_id")
            if field not in event or event[field] is None
        ]

        if missing_fields:
            # Reject events that are missing required identity fields.
            continue

        record = {
            "sequence": sequence,
            "source_system": event["source_system"],
            "actor_id": event["actor_id"],
            "action": event.get("action"),
        }

        if include_provenance:
            record["provenance"] = f"{event['source_system']}:{sequence}"

        # Carry over any additional fields present in the original event,
        # excluding fields already explicitly mapped above.
        reserved_keys = {"sequence", "source_system", "actor_id", "action", "provenance"}
        for key, value in event.items():
            if key not in reserved_keys:
                record[key] = value

        audit_trail.append(record)
        sequence += 1

    return audit_trail
