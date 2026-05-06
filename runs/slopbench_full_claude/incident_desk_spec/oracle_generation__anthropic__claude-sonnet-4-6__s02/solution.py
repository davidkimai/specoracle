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
REASON_MISSING_FIELDS = "missing required fields"
REASON_NO_DEFAULT = "no default rule available"


def route_tickets(tickets: list[dict], rules: dict[str, dict]) -> list[dict]:
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
            lookup_reason = "service match"
        elif "default" in rules:
            rule = rules["default"]
            lookup_reason = "default fallback"
        else:
            # No applicable rule; skip ticket
            continue

        base_priority = int(rule["priority"])
        bonus = severity_bonus_table.get(severity, 0)
        final_priority = base_priority + bonus

        result.append({
            "id": str(ticket_id),
            "queue": rule["queue"],
            "priority": final_priority,
            "status_code": STATUS_ROUTED,
        })

    return result
