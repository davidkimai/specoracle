"""
incident_desk_spec: route_tickets implementation
"""


def route_tickets(
    tickets: list[dict],
    rules: dict[str, dict],
    escalate_after: int | None = None,
) -> list[dict]:
    """
    Route a list of tickets according to the provided rules.

    Parameters
    ----------
    tickets : list[dict]
        Each ticket may contain 'id', 'severity', 'service', and optionally
        'age_minutes' keys.
    rules : dict[str, dict]
        Maps service names to routing configuration dicts with 'queue' and
        'priority'. Must contain a 'default' key for unrecognised services.
    escalate_after : int | None
        If provided, tickets whose 'age_minutes' exceeds this value receive
        3 extra priority points and status_code "escalated".

    Returns
    -------
    list[dict]
        One dict per valid ticket with keys: id, queue, priority, status_code.
    """
    severity_bonus = {
        "critical": 10,
        "high": 5,
    }

    result = []

    for ticket in tickets:
        # Skip tickets missing any required field
        if "id" not in ticket or "severity" not in ticket or "service" not in ticket:
            continue

        ticket_id = ticket["id"]
        severity = ticket["severity"]
        service = ticket["service"]

        # Resolve routing rule
        rule = rules.get(service) or rules.get("default", {})

        queue = rule.get("queue", "")
        base_priority = rule.get("priority", 0)

        # Apply severity bonus
        priority = base_priority + severity_bonus.get(severity, 0)

        # Determine escalation
        status_code = "routed"
        if escalate_after is not None:
            age_minutes = ticket.get("age_minutes")
            if age_minutes is not None and age_minutes > escalate_after:
                priority += 3
                status_code = "escalated"

        result.append({
            "id": ticket_id,
            "queue": queue,
            "priority": priority,
            "status_code": status_code,
        })

    return result
