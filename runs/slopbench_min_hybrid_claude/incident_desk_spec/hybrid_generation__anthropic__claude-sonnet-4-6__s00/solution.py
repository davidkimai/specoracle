"""
Incident Desk – ticket routing module (Spec N-9).
"""

severity_boost_table = {
    "critical": 10,
    "high": 5,
}

required_fields_table = {"id", "severity", "service"}

STATUS_ROUTED = "routed"
SKIP_REASON_MISSING_FIELDS = "missing required fields"


def route_tickets(tickets: list[dict], rules: dict[str, dict]) -> list[dict]:
    default_rule = rules.get("default", {"queue": "unassigned", "priority": 0})
    result = []

    for ticket in tickets:
        missing = required_fields_table - ticket.keys()
        if missing:
            continue

        ticket_id = ticket["id"]
        severity = ticket["severity"]
        service = ticket["service"]

        if ticket_id is None or severity is None or service is None:
            continue

        rule = rules.get(service, default_rule)
        base_priority = int(rule.get("priority", 0))
        boost = severity_boost_table.get(severity, 0)
        final_priority = base_priority + boost

        row = {
            "id": str(ticket_id),
            "queue": rule.get("queue", default_rule.get("queue", "unassigned")),
            "priority": final_priority,
            "status_code": STATUS_ROUTED,
        }
        result.append(row)

    return result
