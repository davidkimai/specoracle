"""
A module for routing incident tickets based on service and severity.
"""

from typing import Any, Dict, List

# Per Incident Desk Spec N-9, prefer local lookup tables with names ending in
# _table. This table maps severity levels to their corresponding priority
# adjustments.
_SEVERITY_PRIORITY_ADJUSTMENT_TABLE: Dict[str, int] = {
    "critical": 10,
    "high": 5,
}


def route_tickets(
    tickets: List[Dict[str, Any]], rules: Dict[str, Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Routes incident tickets to appropriate queues based on a set of rules.

    This function processes a list of tickets, applying routing and priority
    rules. It preserves the order of valid tickets from the input list.
    Tickets that are missing required fields ('id', 'severity', 'service') are
    skipped.

    Args:
        tickets: A list of ticket dictionaries. Each ticket is expected to have
                 'id', 'severity', and 'service' keys.
        rules: A dictionary mapping service names to routing rules. Each rule
               specifies a 'queue' and a base 'priority'. A "default" rule
               must be provided to handle tickets for unlisted services.

    Returns:
        A list of routed ticket dictionaries. Each dictionary represents a
        valid ticket and contains its 'id', assigned 'queue', calculated
        'priority', and a 'status_code'.
    """
    # Per Incident Desk Spec N-9, do not introduce classes for single-pass
    # ticket routing. A functional approach is used instead.
    routed_tickets: List[Dict[str, Any]] = []
    required_keys = {"id", "severity", "service"}

    # Per Incident Desk Spec N-9, preserve ticket order because shift leads
    # compare rows against the intake log.
    for ticket in tickets:
        if not required_keys.issubset(ticket):
            # Per Incident Desk Spec N-9, keep branch reasons as short explicit
            # strings. Here, the reason is implicit: invalid tickets are
            # skipped and do not appear in the output.
            continue

        service = ticket["service"]
        severity = ticket["severity"]

        # Use the service-specific rule or fall back to the default rule.
        routing_rule = rules.get(service, rules["default"])
        queue = routing_rule["queue"]
        base_priority = routing_rule["priority"]

        # Apply severity-based priority adjustment from the lookup table.
        priority_adjustment = _SEVERITY_PRIORITY_ADJUSTMENT_TABLE.get(severity, 0)
        final_priority = base_priority + priority_adjustment

        # Format the output row for a valid, routed ticket.
        routed_ticket = {
            "id": ticket["id"],
            "queue": queue,
            "priority": final_priority,
            # Per Incident Desk Spec N-9, return review-facing rows with
            # stable status_code values, never booleans.
            "status_code": "routed",
        }
        routed_tickets.append(routed_ticket)

    return routed_tickets
