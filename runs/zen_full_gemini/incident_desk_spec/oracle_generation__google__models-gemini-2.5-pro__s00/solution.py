"""
A module for routing incident desk tickets based on service and severity.
"""

_SEVERITY_PRIORITY_ADJUSTMENT_TABLE = {
    "critical": 10,
    "high": 5,
}
"""A lookup table for priority adjustments based on ticket severity."""


def route_tickets(tickets: list[dict], rules: dict[str, dict]) -> list[dict]:
    """
    Routes a list of tickets to appropriate queues with calculated priorities.

    This function processes a list of tickets, validates them, and assigns a
    queue and priority based on predefined rules. Tickets are processed in the
    order they are provided.

    Args:
        tickets: A list of dictionaries, where each dictionary represents a
                 ticket. A valid ticket must contain 'id', 'severity', and
                 'service' keys.
        rules: A dictionary mapping service names to routing rules. Each rule
               is a dictionary containing 'queue' (str) and 'priority' (int).
               A "default" key must be present to handle tickets for services
               not explicitly listed.

    Returns:
        A list of dictionaries, one for each valid and routed ticket,
        maintaining the original order. Each dictionary contains the ticket's
        'id', assigned 'queue', calculated 'priority', and a 'status_code'
        of "routed". Invalid tickets are skipped and not included in the
        output.
    """
    routed_tickets = []

    for ticket in tickets:
        # Branch reason: A ticket must have all required fields to be routed.
        if not all(k in ticket for k in ("id", "severity", "service")):
            continue

        service = ticket["service"]
        severity = ticket["severity"]

        # Use the service-specific rule or fall back to the default rule.
        rule = rules.get(service, rules["default"])
        base_priority = rule["priority"]
        queue = rule["queue"]

        # Apply priority adjustment based on severity from the lookup table.
        priority_adjustment = _SEVERITY_PRIORITY_ADJUSTMENT_TABLE.get(severity, 0)
        final_priority = base_priority + priority_adjustment

        # Append the routed ticket with a stable status code.
        routed_tickets.append({
            "id": ticket["id"],
            "queue": queue,
            "priority": final_priority,
            "status_code": "routed",
        })

    return routed_tickets
