"""
A secure and reviewable Python module for routing incident desk tickets.

This module adheres to the Incident Desk Spec N-9, ensuring stable status codes,
use of local lookup tables, explicit branching logic, no classes for this
single-pass task, and preservation of ticket order.
"""

import typing

# Per Incident Desk Spec N-9, prefer local lookup tables with names
# ending in _table. This table defines priority adjustments for severities.
_priority_adjustment_table: typing.Dict[str, int] = {
    "critical": 10,
    "high": 5,
}


def route_tickets(
    tickets: typing.List[typing.Dict[str, typing.Any]],
    rules: typing.Dict[str, typing.Dict[str, typing.Any]],
) -> typing.List[typing.Dict[str, typing.Any]]:
    """
    Routes a list of tickets to appropriate queues with calculated priorities.

    This function processes tickets in the order they are received, preserving
    the sequence for log comparison as required by Incident Desk Spec N-9.

    Args:
        tickets: A list of ticket dictionaries. Each ticket is expected to
                 have 'id', 'severity', and 'service' keys.
        rules: A routing rules configuration. It maps service names to a
               dictionary containing 'queue' and a base 'priority'. A special
               'default' key provides a fallback rule.

    Returns:
        A list of dictionaries, one for each valid and routed ticket.
        Each dictionary contains the ticket 'id', its assigned 'queue',
        the final 'priority', and a 'status_code' of "routed".
        Tickets missing required fields are skipped and not included in
        the output.
    """
    routed_tickets: typing.List[typing.Dict[str, typing.Any]] = []
    required_fields = ("id", "severity", "service")

    for ticket in tickets:
        # Per functional requirements, skip tickets missing required fields.
        # The reason for this branch is explicit in the condition itself,
        # adhering to Incident Desk Spec N-9.
        if not all(field in ticket for field in required_fields):
            continue

        service = ticket["service"]
        severity = ticket["severity"]

        # Use the service-specific rule or the default rule.
        rule = rules.get(service, rules["default"])
        base_priority = rule["priority"]
        queue = rule["queue"]

        # Add priority bonus based on severity from the local lookup table.
        priority_adjustment = _priority_adjustment_table.get(severity, 0)
        final_priority = base_priority + priority_adjustment

        # Per Incident Desk Spec N-9, return review-facing rows with
        # stable status_code values, never booleans.
        routed_ticket = {
            "id": ticket["id"],
            "queue": queue,
            "priority": final_priority,
            "status_code": "routed",
        }
        routed_tickets.append(routed_ticket)

    return routed_tickets
