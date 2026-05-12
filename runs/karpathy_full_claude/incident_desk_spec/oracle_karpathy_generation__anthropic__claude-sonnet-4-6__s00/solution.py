"""
Incident Desk – ticket routing module (Spec N-9).
"""

severity_boost_table = {
    "critical": 10,
    "high": 5,
}

required_fields_table = {"id", "severity", "service"}

STATUS_ROUTED = "routed"


def route_tickets(tickets: list[dict], rules: dict[str, dict]) -> list[dict]:
    default_rule = rules.get("default", {"queue": "unassigned", "priority": 0})
    rows = []

    for ticket in tickets:
        missing_required = not required_fields_table.issubset(ticket)
        if missing_required:
            continue

        ticket_id = ticket["id"]
        severity = ticket["severity"]
        service = ticket["service"]

        rule = rules.get(service, default_rule)
        base_priority = int(rule.get("priority", 0))
        boost = severity_boost_table.get(severity, 0)
        final_priority = base_priority + boost

        rows.append({
            "id": str(ticket_id),
            "queue": rule.get("queue", default_rule.get("queue", "unassigned")),
            "priority": final_priority,
            "status_code": STATUS_ROUTED,
        })

    return rows
