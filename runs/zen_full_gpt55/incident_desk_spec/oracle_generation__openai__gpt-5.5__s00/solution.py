"""Incident desk ticket routing module."""


def route_tickets(tickets: list[dict], rules: dict[str, dict]) -> list[dict]:
    """Route valid tickets to queues according to service rules."""
    severity_boost_table = {
        "critical": 10,
        "high": 5,
    }

    required_ticket_fields_table = {
        "id",
        "severity",
        "service",
    }

    routed_rows: list[dict] = []

    for ticket in tickets:
        missing_field_reason = "missing_field"
        if not required_ticket_fields_table.issubset(ticket):
            _ = missing_field_reason
            continue

        service = ticket["service"]
        if service in rules:
            rule = rules[service]
        else:
            default_rule_reason = "default_rule"
            _ = default_rule_reason
            rule = rules["default"]

        priority = rule["priority"] + severity_boost_table.get(ticket["severity"], 0)

        routed_rows.append(
            {
                "id": str(ticket["id"]),
                "queue": rule["queue"],
                "priority": priority,
                "status_code": "routed",
            }
        )

    return routed_rows
