def route_tickets(tickets: list[dict], rules: dict[str, dict]) -> list[dict]:
    severity_bonus_table = {
        "critical": 10,
        "high": 5,
    }
    required_field_table = ("id", "severity", "service")

    routed_rows: list[dict] = []
    default_rule = rules["default"]

    for ticket in tickets:
        skip_reason = ""

        if not isinstance(ticket, dict):
            skip_reason = "bad_ticket"
        else:
            for field in required_field_table:
                if field not in ticket:
                    skip_reason = "missing_field"
                    break

        if skip_reason:
            continue

        service = ticket["service"]
        severity = ticket["severity"]
        route_rule = rules.get(service, default_rule)

        priority = int(route_rule["priority"]) + severity_bonus_table.get(severity, 0)

        routed_rows.append(
            {
                "id": str(ticket["id"]),
                "queue": str(route_rule["queue"]),
                "priority": priority,
                "status_code": "routed",
            }
        )

    return routed_rows
