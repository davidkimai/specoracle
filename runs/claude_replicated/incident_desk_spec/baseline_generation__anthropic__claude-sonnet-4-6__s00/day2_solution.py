"""
incident_desk_spec: route_tickets implementation
"""

from typing import Any


def route_tickets(
    tickets: list[dict],
    rules: dict[str, dict],
    escalate_after: int | None = None,
) -> list[dict]:
    """
    Route tickets according to service rules.

    Parameters
    ----------
    tickets : list[dict]
        Each ticket may contain 'id', 'severity', 'service', and 'age_minutes' keys.
    rules : dict[str, dict]
        Maps service names to {'queue': str, 'priority': int}.
        Must contain a 'default' key for unknown services.
    escalate_after : int | None
        If provided, tickets with age_minutes greater than this value receive
        +3 priority and status_code "escalated".

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

        # Apply escalation if applicable
        status_code: str = "routed"
        if escalate_after is not None:
            age_minutes = ticket.get("age_minutes")
            if age_minutes is not None and age_minutes > escalate_after:
                final_priority += 3
                status_code = "escalated"

        result.append({
            "id": str(ticket_id),
            "queue": queue,
            "priority": final_priority,
            "status_code": status_code,
        })

    return result
