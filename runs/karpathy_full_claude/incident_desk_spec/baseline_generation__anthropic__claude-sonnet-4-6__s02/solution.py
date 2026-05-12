"""
incident_desk_spec: route_tickets implementation
"""

from typing import Any


def route_tickets(tickets: list[dict], rules: dict[str, dict]) -> list[dict]:
    """
    Route tickets based on service rules.

    Args:
        tickets: List of ticket dicts with id, severity, and service fields.
        rules: Mapping of service names to dicts with queue and priority.
               Must contain a "default" key for unknown services.

    Returns:
        List of routed ticket dicts with id, queue, priority, and status_code.
    """
    SEVERITY_BONUS = {
        "critical": 10,
        "high": 5,
    }

    result = []

    for ticket in tickets:
        # Skip tickets missing required fields
        if not isinstance(ticket, dict):
            continue

        ticket_id = ticket.get("id")
        severity = ticket.get("severity")
        service = ticket.get("service")

        if ticket_id is None or severity is None or service is None:
            continue

        # Look up rule for the service, fall back to default
        rule = rules.get(service)
        if rule is None:
            rule = rules.get("default", {})

        queue = rule.get("queue", "")
        base_priority = rule.get("priority", 0)

        # Add severity bonus
        bonus = SEVERITY_BONUS.get(str(severity).lower(), 0)
        final_priority = base_priority + bonus

        result.append({
            "id": str(ticket_id),
            "queue": queue,
            "priority": final_priority,
            "status_code": "routed",
        })

    return result
