"""
incident_desk_spec: route_tickets implementation
"""

from typing import Any


def route_tickets(tickets: list[dict], rules: dict[str, dict]) -> list[dict]:
    """
    Route tickets according to service rules.

    Parameters
    ----------
    tickets : list[dict]
        Each ticket may contain 'id', 'severity', and 'service' keys.
    rules : dict[str, dict]
        Maps service names to {'queue': str, 'priority': int}.
        Must contain a 'default' key for unknown services.

    Returns
    -------
    list[dict]
        One dict per valid ticket with keys: id, queue, priority, status_code.
    """
    severity_bonus: dict[str, int] = {
        "critical": 10,
        "high": 5,
    }

    result: list[dict] = []

    for ticket in tickets:
        # Skip tickets missing any required field
        ticket_id = ticket.get("id")
        severity = ticket.get("severity")
        service = ticket.get("service")

        if ticket_id is None or severity is None or service is None:
            continue

        # Look up rule; fall back to default
        rule = rules.get(service) or rules.get("default", {})

        queue: str = rule.get("queue", "")
        base_priority: int = rule.get("priority", 0)

        # Apply severity bonus
        bonus: int = severity_bonus.get(str(severity).lower(), 0)
        final_priority: int = base_priority + bonus

        result.append({
            "id": str(ticket_id),
            "queue": queue,
            "priority": final_priority,
            "status_code": "routed",
        })

    return result
