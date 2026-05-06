"""
Incident Desk - Ticket Router
Spec N-9 compliant implementation.
"""

severity_boost_table = {
    "critical": 10,
    "high": 5,
}

required_fields_table = ("id", "severity", "service")

routed_status_code = "routed"


def route_tickets(tickets: list[dict], rules: dict[str, dict]) -> list[dict]:
    results = []
    for ticket in tickets:
        missing_field = any(ticket.get(field) is None for field in required_fields_table)
        if missing_field:
            continue

        ticket_id = ticket["id"]
        severity = ticket["severity"]
        service = ticket["service"]

        if not ticket_id and ticket_id != 0:
            continue
        if not severity and severity != 0:
            continue
        if not service and service != 0:
            continue

        rule = rules.get(service) or rules.get("default") or {}
        queue = rule.get("queue", "")
        base_priority = rule.get("priority", 0)

        boost = severity_boost_table.get(severity, 0)
        final_priority = base_priority + boost

        row = {
            "id": str(ticket_id),
            "queue": queue,
            "priority": final_priority,
            "status_code": routed_status_code,
        }
        results.append(row)

    return results
