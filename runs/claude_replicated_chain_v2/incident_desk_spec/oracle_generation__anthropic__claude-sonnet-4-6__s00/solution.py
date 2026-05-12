"""
Incident Desk – ticket routing module (Spec N-9).
"""

severity_boost_table = {
    "critical": 10,
    "high": 5,
}

STATUS_ROUTED = "routed"
REASON_MISSING_FIELDS = "missing required fields"
REQUIRED_FIELDS = ("id", "severity", "service")


def route_tickets(tickets: list[dict], rules: dict[str, dict]) -> list[dict]:
    default_rule = rules.get("default", {"queue": "default", "priority": 0})
    result = []

    for ticket in tickets:
        missing = any(ticket.get(field) is None for field in REQUIRED_FIELDS)
        if missing:
            continue

        ticket_id = ticket["id"]
        severity = ticket["severity"]
        service = ticket["service"]

        if not ticket_id and ticket_id != 0:
            continue

        rule = rules.get(service, default_rule)
        queue = rule["queue"]
        base_priority = rule["priority"]

        boost = severity_boost_table.get(severity, 0)
        priority = base_priority + boost

        result.append({
            "id": str(ticket_id),
            "queue": queue,
            "priority": priority,
            "status_code": STATUS_ROUTED,
        })

    return result
