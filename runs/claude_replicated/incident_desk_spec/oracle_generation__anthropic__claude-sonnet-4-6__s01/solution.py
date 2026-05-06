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

        result.append({
            "id": str(ticket_id),
            "queue": queue,
            "priority": priority,
            "status_code": ROUTED_STATUS,
        })

    return result
