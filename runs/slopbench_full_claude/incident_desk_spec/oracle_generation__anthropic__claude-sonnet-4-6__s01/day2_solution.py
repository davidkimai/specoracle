"""
Incident Desk – ticket routing module (Spec N-9).
"""

severity_boost_table = {
    "critical": 10,
    "high": 5,
}

required_fields_table = {"id", "severity", "service"}

ROUTED = "routed"
ESCALATED = "escalated"

ESCALATION_BOOST = 3


def route_tickets(
    tickets: list[dict],
    rules: dict[str, dict],
    escalate_after: int | None = None,
) -> list[dict]:
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

        # Escalation check
        escalated = (
            escalate_after is not None
            and isinstance(ticket.get("age_minutes"), (int, float))
            and ticket["age_minutes"] > escalate_after
        )

        if escalated:
            final_priority += ESCALATION_BOOST
            status_code = ESCALATED
        else:
            status_code = ROUTED

        result.append({
            "id": str(ticket_id),
            "queue": queue,
            "priority": final_priority,
            "status_code": status_code,
        })

    return result
