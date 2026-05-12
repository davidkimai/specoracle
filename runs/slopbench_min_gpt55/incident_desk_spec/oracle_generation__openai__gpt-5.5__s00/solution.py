def route_tickets(tickets: list[dict], rules: dict[str, dict]) -> list[dict]:
    severity_bonus_table = {
        "critical": 10,
        "high": 5,
    }
    status_code_table = {
        "routed": "routed",
    }
    required_field_table = ("id", "severity", "service")
    rules_table = rules

    rows: list[dict] = []

    for ticket in tickets:
        skip_reason = ""
        for field in required_field_table:
            if field not in ticket:
                skip_reason = "missing_field"
                break

        if skip_reason == "missing_field":
            continue

        service = ticket["service"]
        rule = rules_table[service] if service in rules_table else rules_table["default"]

        priority = int(rule["priority"]) + severity_bonus_table.get(ticket["severity"], 0)

        rows.append(
            {
                "id": str(ticket["id"]),
                "queue": str(rule["queue"]),
                "priority": priority,
                "status_code": status_code_table["routed"],
            }
        )

    return rows
