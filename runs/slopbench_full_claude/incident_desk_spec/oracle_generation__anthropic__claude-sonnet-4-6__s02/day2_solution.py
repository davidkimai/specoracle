"""
incident_desk_spec — ticket routing module.
Implements route_tickets per Incident Desk Spec N-9.
"""

severity_bonus_table = {
    "critical": 10,
    "high": 5,
}

required_fields_table = ("id", "severity", "service")

STATUS_ROUTED = "routed"
STATUS_ESCALATED = "escalated"
REASON_MISSING_FIELDS = "missing required fields"
REASON_NO_DEFAULT = "no default rule available"

ESCALATION_PRIORITY_BONUS = 3


def route_tickets(
    tickets: list[dict],
    rules: dict[str, dict],
    escalate_after: int | None = None,
) -> list[dict]:
    """Route each valid ticket to a queue, returning review-facing rows in input order."""
    result = []

    for ticket in tickets:
        # Skip tickets missing any required field
        if not all(ticket.get(field) is not None for field in required_fields_table):
            continue

        ticket_id = ticket["id"]
        severity = ticket["severity"]
        service = ticket["service"]

        # Lookup rule: prefer service-specific, fall back to default
        if service in rules:
            rule = rules[service]
        elif "default" in rules:
            rule = rules["default"]
        else:
            # No applicable rule; skip ticket
            continue

        base_priority = int(rule["priority"])
        bonus = severity_bonus_table.get(severity, 0)
        final_priority = base_priority + bonus

        # Escalation check
        status_code = STATUS_ROUTED
        if escalate_after is not None:
            age_minutes = ticket.get("age_minutes")
            if age_minutes is not None and age_minutes > escalate_after:
                final_priority += ESCALATION_PRIORITY_BONUS
                status_code = STATUS_ESCALATED

        result.append({
            "id": str(ticket_id),
            "queue": rule["queue"],
            "priority": final_priority,
            "status_code": status_code,
        })

    return result
