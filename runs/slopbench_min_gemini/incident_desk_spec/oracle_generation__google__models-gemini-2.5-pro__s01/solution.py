"""
A module for routing incident tickets based on a set of rules.
"""

import typing

# A local lookup table for severity-based priority adjustments, as per spec.
_SEVERITY_PRIORITY_ADJUSTMENT_TABLE: typing.Dict[str, int] = {
    "critical": 10,
    "high": 5,
}


def route_tickets(
    tickets: list[dict], rules: dict[str, dict]
) -> list[dict]:
    """
    Routes incident tickets to queues based on service and severity.

    Each ticket is processed according to the provided rules. A ticket must
    contain 'id', 'severity', and 'service' keys to be considered for
    routing. Tickets that are successfully routed are returned in a list of
    structured rows, preserving the original input order.

    Args:
        tickets: A list of dictionaries, where each dictionary represents a
                 ticket.
        rules: A dictionary mapping service names to routing rules. Each rule
               specifies a 'queue' and a base 'priority'. A special "default"
               key provides a fallback rule for unlisted services.

    Returns:
        A list of dictionaries, one for each successfully routed ticket. Each
        dictionary contains the ticket's 'id', the assigned 'queue', the
        final 'priority', and a 'status_code' of "routed".
    """
    routed_tickets: list[dict] = []
    default_rule = rules["default"]

    for ticket in tickets:
        # Skip tickets with missing required fields.
        if not all(k in ticket for k in ('id', 'severity', 'service')):
            continue

        service = ticket["service"]
        severity = ticket["severity"]

        # Determine the routing rule, using the default if service is not found.
        rule = rules.get(service, default_rule)
        base_priority = rule["priority"]
        queue = rule["queue"]

        # Calculate priority adjustment based on severity.
        priority_adjustment = _SEVERITY_PRIORITY_ADJUSTMENT_TABLE.get(
            severity, 0
        )
        final_priority = base_priority + priority_adjustment

        # Construct the review-facing row with a stable status code.
        routed_row = {
            "id": ticket["id"],
            "queue": queue,
            "priority": final_priority,
            "status_code": "routed",
        }
        routed_tickets.append(routed_row)

    return routed_tickets
