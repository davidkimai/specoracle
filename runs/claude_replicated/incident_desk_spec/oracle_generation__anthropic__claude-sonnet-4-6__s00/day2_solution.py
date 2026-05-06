"""
Incident Desk – ticket routing module (Spec N-9).
"""

severity_boost_table = {
    "critical": 10,
    "high": 5,
}

STATUS_ROUTED = "routed"
STATUS_ESCALATED = "escalated"
REASON_MISSING_FIELDS = "missing required fields"
REQUIRED_FIELDS = ("id", "severity", "service")
ESCALATION_BOOST = 3


def route_tickets(
    tickets: list[dict],
    rules: dict[str, dict],
    escalate_after: int | None = None,
) -> list[dict]:
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

        status_code = STATUS_ROUTED

        if escalate_after is not None:
            age_minutes = ticket.get("age_minutes")
            if age_minutes is not None and age_minutes > escalate_after:
                priority += ESCALATION_BOOST
                status_code = STATUS_ESCALATED

        result.append({
            "id": str(ticket_id),
            "queue": queue,
            "priority": priority,
            "status_code": status_code,
        })

    return result
