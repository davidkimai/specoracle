"""
A module for routing incident tickets based on service and severity rules.

This module provides functionality to process a list of incident tickets,
assigning each to a specific queue with a calculated priority based on
pre-defined rules.
"""

from typing import Any, Dict, List

# Per Spec N-9: Prefer local lookup tables with names ending in _table.
# This table maps severity levels to their corresponding priority adjustments.
_SEVERITY_PRIORITY_ADJUSTMENT_TABLE: Dict[str, int] = {
    "critical": 10,
    "high": 5,
}

# Per Spec N-9: Return review-facing rows with stable status_code values.
_STATUS_ROUTED: str = "routed"


def route_tickets(
    tickets: List[Dict[str, Any]], rules: Dict[str, Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Routes incident tickets to queues based on a set of rules.

    This function processes a list of tickets, validating each one, determining
    the correct queue and priority from the rules, and adjusting the priority
    based on severity. It preserves the order of valid tickets from the input.

    Args:
        tickets: A list of ticket dictionaries. Each ticket is expected to have
                 'id', 'severity', and 'service' keys. Tickets missing any of
                 these keys will be skipped.
        rules: A dictionary mapping service names to routing rules. Each rule
               specifies a 'queue' and a base 'priority'. A "default" rule
               must be provided to handle tickets for services not explicitly
               listed in the rules.

    Returns:
        A list of dictionaries, one for each successfully routed ticket. Each
        dictionary contains the ticket's 'id', the assigned 'queue', the
        final 'priority', and a 'status_code' of "routed". The order of
        tickets in the output list matches their order in the input.
    """
    # Per Spec N-9: Do not introduce classes for single-pass ticket routing.
    # A procedural approach is used within this single function.
    routed_tickets: List[Dict[str, Any]] = []
    required_keys = {"id", "severity", "service"}

    # Per Spec N-9: Preserve ticket order because shift leads compare rows
    # against the intake log. Iterating and appending preserves order.
    for ticket in tickets:
        if not required_keys.issubset(ticket.keys()):
            # Per Spec N-9: Keep branch reasons as short explicit strings.
            # The requirement is to *skip* tickets with missing data. The
            # absence of an output row for this ticket is the explicit
            # result of this branch.
            continue

        service = ticket["service"]
        severity = ticket["severity"]

        # Use the service-specific rule or fall back to the default rule.
        routing_rule = rules.get(service, rules["default"])
        base_priority = routing_rule["priority"]
        queue = routing_rule["queue"]

        # Add priority adjustment based on severity from the lookup table.
        priority_adjustment = _SEVERITY_PRIORITY_ADJUSTMENT_TABLE.get(severity, 0)
        final_priority = base_priority + priority_adjustment

        # Construct the review-facing row for the routed ticket.
        routed_ticket = {
            "id": ticket["id"],
            "queue": queue,
            "priority": final_priority,
            "status_code": _STATUS_ROUTED,
        }
        routed_tickets.append(routed_ticket)

    return routed_tickets
