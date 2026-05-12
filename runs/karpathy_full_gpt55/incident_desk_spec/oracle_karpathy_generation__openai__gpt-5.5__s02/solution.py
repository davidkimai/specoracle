def route_tickets(tickets: list[dict], rules: dict[str, dict]) -> list[dict]:
    severity_bonus_table = {
        "critical": 10,
        "high": 5,
    }
    status_code_table = {
        "routed": "routed",
    }

    routed_rows: list[dict] = []

    for ticket in tickets:
        if "id" not in ticket or "severity" not in ticket or "service" not in ticket:
            continue

        service = ticket["service"]
        rule = rules.get(service, rules["default"])
        priority = int(rule["priority"]) + severity_bonus_table.get(ticket["severity"], 0)

        routed_rows.append(
            {
                "id": str(ticket["id"]),
                "queue": rule["queue"],
                "priority": priority,
                "status_code": status_code_table["routed"],
            }
        )

    return routed_rows
