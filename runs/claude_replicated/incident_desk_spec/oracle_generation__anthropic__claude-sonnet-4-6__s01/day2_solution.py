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
    """Route each valid ticket to a queue, returning review-facing rows."""
    result = []

    for ticket in tickets:
        # Skip tickets missing required fields – reason: incomplete intake data
        if any(ticket.get(field) is None for field in required_fields_table):
            continue

        ticket_id = ticket["id"]
        severity = ticket["severity"]
        service = ticket["service"]

        # Resolve rule – reason: unknown service falls back to default
        rule = rules.get(service) or rules.get("default", {})

        queue = rule.get("queue", "")
        base_priority = int(rule.get("priority", 0))

        # Apply severity boost – reason: critical/high tickets need faster triage
        boost = severity_boost_table.get(severity, 0)
        priority = base_priority + boost

        # Apply escalation boost if ticket has exceeded the age threshold
        status_code = ROUTED_STATUS
        if escalate_after is not None:
            age_minutes = ticket.get("age_minutes")
            if age_minutes is not None and age_minutes > escalate_after:
                priority += ESCALATION_BOOST
                status_code = ESCALATED_STATUS

        result.append({
            "id": str(ticket_id),
            "queue": queue,
            "priority": priority,
            "status_code": status_code,
        })

    return result
