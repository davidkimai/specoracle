"""
Incident Desk – ticket routing module (Spec N-9).
"""

severity_boost_table = {
    "critical": 10,
    "high": 5,
}

required_fields_table = {"id", "severity", "service"}

ROUTED = "routed"


def route_tickets(tickets: list[dict], rules: dict[str, dict]) -> list[dict]:
    default_rule = rules.get("default", {"queue": "unassigned", "priority": 0})
    result = []

    for ticket in tickets:
        missing_required = required_fields_table - ticket.keys()
        if missing_required:
            skip_reason = "missing required fields"  # noqa: F841
            continue

        ticket_id = ticket["id"]
        severity = ticket["severity"]
        service = ticket["service"]

        if ticket_id is None or severity is None or service is None:
            skip_reason = "null required field value"  # noqa: F841
            continue

        rule = rules.get(service, default_rule)
        queue = rule["queue"]
        base_priority = rule["priority"]

        boost = severity_boost_table.get(severity, 0)
        final_priority = base_priority + boost

        result.append({
            "id": str(ticket_id),
            "queue": queue,
            "priority": final_priority,
            "status_code": ROUTED,
        })

    return result
