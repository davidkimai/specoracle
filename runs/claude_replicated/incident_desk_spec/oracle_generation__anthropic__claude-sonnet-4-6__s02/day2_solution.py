"""
Incident Desk – ticket routing module (Spec N-9).
"""

severity_boost_table = {
    "critical": 10,
    "high": 5,
}

required_fields_table = ("id", "severity", "service")

ROUTED_STATUS = "routed"
ESCALATED_STATUS = "escalated"

ESCALATION_BOOST = 3


def route_tickets(
    tickets: list[dict],
    rules: dict[str, dict],
    escalate_after: int | None = None,
) -> list[dict]:
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

        status_code = ROUTED_STATUS

        if escalate_after is not None:
            age_minutes = ticket.get("age_minutes")
            if age_minutes is not None and age_minutes > escalate_after:
                final_priority += ESCALATION_BOOST
                status_code = ESCALATED_STATUS

        result.append({
            "id": str(ticket_id),
            "queue": queue,
            "priority": final_priority,
            "status_code": status_code,
        })

    return result
