from __future__ import annotations


def route_tickets(tickets: list[dict], rules: dict[str, dict]) -> list[dict]:
    required_field_table = ("id", "severity", "service")
    severity_bonus_table = {
        "critical": 10,
        "high": 5,
    }
    status_code_table = {
        "routed": "routed",
    }
    fallback_table = {
        "service": "default",
    }

    routed_rows: list[dict] = []
    default_rule = rules[fallback_table["service"]]

    for ticket in tickets:
        skip_reason = ""
        if any(field not in ticket for field in required_field_table):
            skip_reason = "missing_field"

        if skip_reason == "missing_field":
            continue

        service = ticket["service"]
        rule = rules.get(service, default_rule)
        priority = int(rule["priority"]) + severity_bonus_table.get(ticket["severity"], 0)

        routed_rows.append(
            {
                "id": str(ticket["id"]),
                "queue": str(rule["queue"]),
                "priority": priority,
                "status_code": status_code_table["routed"],
            }
        )

    return routed_rows
