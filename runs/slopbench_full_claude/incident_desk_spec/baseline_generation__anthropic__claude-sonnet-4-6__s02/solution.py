"""
incident_desk_spec: route_tickets implementation
"""

from __future__ import annotations


def route_tickets(tickets: list[dict], rules: dict[str, dict]) -> list[dict]:
    """Route tickets according to service rules.

    Args:
        tickets: List of ticket dicts, each expected to have 'id', 'severity',
                 and 'service' keys.
        rules: Mapping of service names to routing configuration dicts with
               'queue' and 'priority' keys. Must include a 'default' entry.

    Returns:
        List of routed ticket dicts for every valid input ticket, in input order.
    """
    severity_bonus: dict[str, int] = {
        "critical": 10,
        "high": 5,
    }

    result: list[dict] = []

    for ticket in tickets:
        # Skip tickets missing required fields
        ticket_id = ticket.get("id")
        severity = ticket.get("severity")
        service = ticket.get("service")

        if ticket_id is None or severity is None or service is None:
            continue

        # Look up rule for the service, fall back to default
        rule = rules.get(service) or rules.get("default", {})

        queue: str = rule.get("queue", "")
        base_priority: int = rule.get("priority", 0)

        bonus: int = severity_bonus.get(str(severity).lower(), 0)
        final_priority: int = base_priority + bonus

        result.append({
            "id": str(ticket_id),
            "queue": queue,
            "priority": final_priority,
            "status_code": "routed",
        })

    return result
