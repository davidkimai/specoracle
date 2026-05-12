from typing import Any

__all__ = ["route_tickets"]


def route_tickets(tickets: list[dict], rules: dict[str, dict]) -> list[dict]:
    severity_bonus_table = {
        "critical": 10,
        "high": 5,
    }

    required_field_table = {
        "id": "missing_id",
        "severity": "missing_severity",
        "service": "missing_service",
    }

    routed_rows: list[dict[str, Any]] = []

    for ticket in tickets:
        skip_reason = ""
        for field_name, reason in required_field_table.items():
            if field_name not in ticket:
                skip_reason = reason
                break

        if skip_reason:
            continue

        service = ticket["service"]
        rule = rules.get(service, rules["default"])
        base_priority = int(rule["priority"])
        priority = base_priority + severity_bonus_table.get(ticket["severity"], 0)

        routed_rows.append(
            {
                "id": str(ticket["id"]),
                "queue": str(rule["queue"]),
                "priority": priority,
                "status_code": "routed",
            }
        )

    return routed_rows
