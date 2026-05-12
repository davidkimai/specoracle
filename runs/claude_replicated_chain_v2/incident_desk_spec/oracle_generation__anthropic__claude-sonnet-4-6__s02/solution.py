"""
Incident Desk – ticket routing module (Spec N-9).
"""

severity_boost_table = {
    "critical": 10,
    "high": 5,
}

required_fields_table = ("id", "severity", "service")

ROUTED_STATUS = "routed"


def route_tickets(tickets: list[dict], rules: dict[str, dict]) -> list[dict]:
    """Route each valid ticket to a queue based on service rules and severity."""
    default_rule = rules.get("default", {"queue": "unassigned", "priority": 0})
    result = []

    for ticket in tickets:
        missing_required = any(ticket.get(field) is None for field in required_fields_table)
        if missing_required:
            continue

        ticket_id = ticket["id"]
        severity = ticket["severity"]
        service = ticket["service"]

        rule = rules.get(service, default_rule)
        queue = rule["queue"]
        base_priority = rule["priority"]

        boost = severity_boost_table.get(severity, 0)
        final_priority = base_priority + boost

        result.append({
            "id": str(ticket_id),
            "queue": queue,
            "priority": final_priority,
            "status_code": ROUTED_STATUS,
        })

    return result
