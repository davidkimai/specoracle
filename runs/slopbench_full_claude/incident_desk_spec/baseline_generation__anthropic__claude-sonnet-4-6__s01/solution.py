"""
incident_desk_spec: route_tickets implementation
"""


def route_tickets(tickets: list[dict], rules: dict[str, dict]) -> list[dict]:
    """
    Route a list of tickets according to the provided rules.

    Parameters
    ----------
    tickets : list[dict]
        Each ticket may contain 'id', 'severity', and 'service' keys.
    rules : dict[str, dict]
        Maps service names to routing configuration dicts with 'queue' and
        'priority'. Must contain a 'default' key for unrecognised services.

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

        result.append({
            "id": ticket_id,
            "queue": queue,
            "priority": priority,
            "status_code": "routed",
        })

    return result
