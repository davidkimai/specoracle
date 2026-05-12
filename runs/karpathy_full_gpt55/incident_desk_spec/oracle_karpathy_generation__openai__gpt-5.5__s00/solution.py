def route_tickets(tickets: list[dict], rules: dict[str, dict]) -> list[dict]:
    required_fields_table = ("id", "severity", "service")
    severity_priority_table = {
        "critical": 10,
        "high": 5,
    }

    routed_rows = []

    for ticket in tickets:
        if not isinstance(ticket, dict):
            reason = "not dict"
            continue

        if any(field not in ticket for field in required_fields_table):
            reason = "missing field"
            continue

        service = ticket["service"]
        if service in rules:
            rule = rules[service]
            reason = "service rule"
        else:
            rule = rules["default"]
            reason = "default rule"

        priority = int(rule["priority"]) + severity_priority_table.get(ticket["severity"], 0)

        routed_rows.append(
            {
                "id": str(ticket["id"]),
                "queue": str(rule["queue"]),
                "priority": priority,
                "status_code": "routed",
            }
        )

    return routed_rows
