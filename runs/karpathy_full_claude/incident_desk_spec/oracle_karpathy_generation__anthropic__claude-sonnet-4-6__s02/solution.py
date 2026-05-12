"""
Incident Desk - Ticket Router
Spec N-9 compliant implementation.
"""

severity_boost_table = {
    "critical": 10,
    "high": 5,
}

REQUIRED_FIELDS = ("id", "severity", "service")

STATUS_ROUTED = "routed"
REASON_MISSING_FIELDS = "missing required fields"
REASON_NO_DEFAULT = "no default rule available"


def route_tickets(tickets: list[dict], rules: dict[str, dict]) -> list[dict]:
    result = []

    for ticket in tickets:
        # Skip tickets missing any required field
        if not all(field in ticket for field in REQUIRED_FIELDS):
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
            continue

        queue = rule["queue"]
        base_priority = rule["priority"]

        boost = severity_boost_table.get(severity, 0)
        final_priority = base_priority + boost

        result.append({
            "id": str(ticket_id),
            "queue": queue,
            "priority": final_priority,
            "status_code": STATUS_ROUTED,
        })

    return result
