"""
incident_desk_spec - Route support tickets to appropriate queues.
"""

from __future__ import annotations


def route_tickets(tickets: list[dict], rules: dict[str, dict]) -> list[dict]:
    """Route tickets according to service rules.

    Parameters
    ----------
    tickets:
        List of ticket dicts, each potentially containing 'id', 'severity',
        and 'service' keys.
    rules:
        Mapping of service name -> {'queue': str, 'priority': int}.
        Must contain a 'default' key used when a ticket's service is absent.

    Returns
    -------
    list[dict]
        One dict per valid ticket in input order with keys:
        'id', 'queue', 'priority', 'status_code'.
    """
    severity_bonus: dict[str, int] = {
        "critical": 10,
        "high": 5,
    }

    result: list[dict] = []

    for ticket in tickets:
        # Validate required fields
        ticket_id = ticket.get("id")
        severity = ticket.get("severity")
        service = ticket.get("service")

        if ticket_id is None or severity is None or service is None:
            continue

        # Resolve routing rule
        rule = rules.get(service) or rules.get("default", {})
        queue = rule.get("queue", "")
        base_priority = rule.get("priority", 0)

        # Apply severity bonus
        bonus = severity_bonus.get(severity, 0)
        final_priority = base_priority + bonus

        result.append(
            {
                "id": str(ticket_id),
                "queue": queue,
                "priority": final_priority,
                "status_code": "routed",
            }
        )

    return result
