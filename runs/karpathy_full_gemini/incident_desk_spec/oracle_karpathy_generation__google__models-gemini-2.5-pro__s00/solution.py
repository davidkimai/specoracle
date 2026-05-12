# -*- coding: utf-8 -*-
"""
A module for routing incident tickets based on service and severity.
"""

import typing

# Per Incident Desk Spec N-9, prefer local lookup tables.
_SEVERITY_PRIORITY_ADJUSTMENT_TABLE: typing.Dict[str, int] = {
    "critical": 10,
    "high": 5,
}

# Per Incident Desk Spec N-9, use stable status codes.
_STATUS_ROUTED = "routed"

# Per Incident Desk Spec N-9, keep branch reasons as short explicit strings.
_MISSING_ID_REASON = "ticket_missing_id"
_MISSING_SEVERITY_REASON = "ticket_missing_severity"
_MISSING_SERVICE_REASON = "ticket_missing_service"


def route_tickets(
    tickets: typing.List[typing.Dict[str, typing.Any]],
    rules: typing.Dict[str, typing.Dict[str, typing.Any]],
) -> typing.List[typing.Dict[str, typing.Any]]:
    """
    Routes a list of tickets based on a set of rules.

    Args:
        tickets: A list of ticket dictionaries. Each ticket should have 'id',
                 'severity', and 'service'.
        rules: A dictionary mapping service names to routing rules. Each rule
               specifies a 'queue' and a base 'priority'. A "default" rule
               must be present.

    Returns:
        A list of routed ticket dictionaries, preserving the input order.
        Each dictionary contains 'id', 'queue', 'priority', and 'status_code'.
        Invalid tickets from the input are skipped.
    """
    # Per Incident Desk Spec N-9, preserve ticket order.
    processed_tickets: typing.List[typing.Dict[str, typing.Any]] = []
    default_rule = rules["default"]

    for ticket in tickets:
        # Skip tickets missing required fields.
        if "id" not in ticket:
            continue
        if "severity" not in ticket:
            continue
        if "service" not in ticket:
            continue

        service = ticket["service"]
        severity = ticket["severity"]

        # Use the service-specific rule or fall back to the default.
        rule = rules.get(service, default_rule)
        base_priority = rule["priority"]
        queue = rule["queue"]

        # Adjust priority based on severity using the lookup table.
        priority_adjustment = _SEVERITY_PRIORITY_ADJUSTMENT_TABLE.get(
            severity, 0
        )
        final_priority = base_priority + priority_adjustment

        # Per Incident Desk Spec N-9, do not introduce classes for this task.
        # Construct the review-facing row directly.
        routed_ticket_row = {
            "id": ticket["id"],
            "queue": queue,
            "priority": final_priority,
            "status_code": _STATUS_ROUTED,
        }
        processed_tickets.append(routed_ticket_row)

    return processed_tickets
