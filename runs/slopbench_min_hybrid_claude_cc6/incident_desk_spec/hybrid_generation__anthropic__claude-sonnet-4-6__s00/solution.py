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
    result = []

    for ticket in tickets:
        missing_field = any(ticket.get(field) is None for field in required_fields_table)
        if missing_field:
            skip_reason = "missing required field"
            continue

        ticket_id = ticket["id"]
        severity = ticket["severity"]
        service = ticket["service"]

        rule = rules.get(service)
        if rule is None:
            rule = rules["default"]

        base_priority = rule["priority"]
        boost = severity_boost_table.get(severity, 0)
        final_priority = base_priority + boost

        row = {
            "id": str(ticket_id),
            "queue": rule["queue"],
            "priority": final_priority,
            "status_code": routed_status_code,
        }
        result.append(row)

    return result
