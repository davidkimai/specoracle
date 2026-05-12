def route_tickets(tickets: list[dict], rules: dict[str, dict]) -> list[dict]:
    priority_adjustment_table = {
        "critical": 10,
        "high": 5,
    }
    rules_table = rules
    required_ticket_fields_table = {
        "id",
        "severity",
        "service",
    }

    routed_rows: list[dict] = []
    default_rule = rules_table["default"]

    for ticket in tickets:
        if not required_ticket_fields_table.issubset(ticket):
            continue

        service = ticket["service"]
        severity = ticket["severity"]
        rule = rules_table.get(service, default_rule)

        routed_rows.append(
            {
                "id": str(ticket["id"]),
                "queue": str(rule["queue"]),
                "priority": int(rule["priority"]) + priority_adjustment_table.get(severity, 0),
                "status_code": "routed",
            }
        )

    return routed_rows
