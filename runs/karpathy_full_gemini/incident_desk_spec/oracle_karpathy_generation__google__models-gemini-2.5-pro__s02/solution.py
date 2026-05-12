"""
A module for routing incident tickets based on service and severity.

This module provides functionality to process a list of incident tickets,
applying a set of routing rules to determine the appropriate queue and
priority for each ticket.
"""

from typing import Dict, List, Any

# A local lookup table for severity-based priority adjustments, as per spec.
_SEVERITY_PRIORITY_ADJUSTMENT_TABLE: Dict[str, int] = {
    "critical": 10,
    "high": 5,
}


def route_tickets(
    tickets: List[Dict[str, Any]], rules: Dict[str, Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Routes a list of tickets to queues based on a set of rules.

    For each ticket, this function determines the destination queue and priority
    based on the ticket's service. It also adjusts the priority based on the
    ticket's severity.

    Tickets that are missing 'id', 'severity', or 'service' fields are skipped.
    The order of the returned routed tickets is preserved from the input list.

    Args:
        tickets: A list of dictionaries, where each dictionary represents a
                 ticket with at least 'id', 'severity', and 'service'.
        rules: A dictionary mapping service names to routing rules. Each rule
               is a dictionary with 'queue' and 'priority'. A special "default"
               key must be present to handle tickets for services not
               explicitly listed.

    Returns:
        A list of dictionaries, one for each valid and routed ticket. Each
        dictionary contains 'id', 'queue', 'priority', and 'status_code'.
    """
    routed_tickets: List[Dict[str, Any]] = []
    required_keys = ("id", "severity", "service")

    for ticket in tickets:
        # Skip tickets that are missing any of the required fields.
        if not all(key in ticket for key in required_keys):
            continue

        service = ticket["service"]
        severity = ticket["severity"]

        # Look up the routing rule for the service, falling back to default.
        rule = rules.get(service, rules["default"])
        base_priority = rule["priority"]

        # Determine the priority adjustment from the severity lookup table.
        priority_adjustment = _SEVERITY_PRIORITY_ADJUSTMENT_TABLE.get(severity, 0)

        # Construct the final routed ticket data.
        final_priority = base_priority + priority_adjustment
        output_row = {
            "id": ticket["id"],
            "queue": rule["queue"],
            "priority": final_priority,
            "status_code": "routed",  # Stable status_code value, per spec.
        }
        routed_tickets.append(output_row)

    return routed_tickets
