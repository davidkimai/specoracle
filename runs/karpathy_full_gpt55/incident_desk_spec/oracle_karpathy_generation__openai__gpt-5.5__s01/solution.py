__all__ = ["route_tickets"]


def route_tickets(tickets: list[dict], rules: dict[str, dict]) -> list[dict]:
    required_fields_table = ("id", "severity", "service")
    severity_boost_table = {
        "critical": 10,
        "high": 5,
    }

    routed_rows = []

    for ticket in tickets:
        skip_reason = ""

        if not isinstance(ticket, dict):
            skip_reason = "not_dict"
        elif any(field not in ticket for field in required_fields_table):
            skip_reason = "missing_field"

        if skip_reason:
            continue

        service = ticket["service"]
        rule = rules[service] if service in rules else rules["default"]
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
