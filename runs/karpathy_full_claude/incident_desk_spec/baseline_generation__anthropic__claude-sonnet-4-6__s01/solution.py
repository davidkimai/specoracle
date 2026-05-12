"""
incident_desk_spec: Route support tickets to queues based on rules.
"""


def route_tickets(tickets: list[dict], rules: dict[str, dict]) -> list[dict]:
    """
    Route tickets to queues based on service rules.

    Args:
        tickets: List of ticket dicts with id, severity, and service fields.
        rules: Mapping of service names to dicts with queue and priority.
               Must include a "default" key for unknown services.

    Returns:
        List of routed ticket dicts with id, queue, priority, and status_code.
    """
    severity_bonus = {
        "critical": 10,
        "high": 5,
    }

    result = []

    for ticket in tickets:
        # Skip tickets missing required fields
        ticket_id = ticket.get("id")
        severity = ticket.get("severity")
        service = ticket.get("service")

        if ticket_id is None or severity is None or service is None:
            continue

        # Look up rule for service, fall back to default
        rule = rules.get(service, rules.get("default", {}))

        queue = rule.get("queue", "")
        base_priority = rule.get("priority", 0)

        # Add severity bonus
        bonus = severity_bonus.get(severity, 0)
        final_priority = base_priority + bonus

        result.append({
            "id": str(ticket_id),
            "queue": queue,
            "priority": final_priority,
            "status_code": "routed",
        })

    return result
