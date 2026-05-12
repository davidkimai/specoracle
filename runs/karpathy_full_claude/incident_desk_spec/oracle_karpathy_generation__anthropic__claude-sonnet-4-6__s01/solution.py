"""
Incident Desk – ticket routing module (Spec N-9).
"""

severity_boost_table = {
    "critical": 10,
    "high": 5,
}

required_fields_table = ("id", "severity", "service")

STATUS_ROUTED = "routed"


def route_tickets(tickets: list[dict], rules: dict[str, dict]) -> list[dict]:
    results = []

    for ticket in tickets:
        missing_required = any(
            ticket.get(field) is None or ticket.get(field) == ""
            for field in required_fields_table
        )
        if missing_required:
            continue

        ticket_id = ticket["id"]
        severity = ticket["severity"]
        service = ticket["service"]

        rule = rules.get(service) or rules.get("default") or {}
        queue = rule.get("queue", "")
        base_priority = int(rule.get("priority", 0))

        boost = severity_boost_table.get(severity, 0)
        final_priority = base_priority + boost

        results.append({
            "id": str(ticket_id),
            "queue": queue,
            "priority": final_priority,
            "status_code": STATUS_ROUTED,
        })

    return results
