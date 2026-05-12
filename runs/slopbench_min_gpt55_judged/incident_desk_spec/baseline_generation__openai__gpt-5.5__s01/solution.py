from typing import Any


def route_tickets(tickets: list[dict], rules: dict[str, dict]) -> list[dict]:
    routed: list[dict[str, Any]] = []

    for ticket in tickets:
        if not isinstance(ticket, dict):
            continue

        if "id" not in ticket or "severity" not in ticket or "service" not in ticket:
            continue

        service = ticket["service"]
        rule = rules.get(service, rules.get("default"))
        if not isinstance(rule, dict):
            continue

        queue = rule.get("queue")
        priority = rule.get("priority")

        try:
            adjusted_priority = int(priority)
        except (TypeError, ValueError):
            continue

        severity = ticket["severity"]
        if severity == "critical":
            adjusted_priority += 10
        elif severity == "high":
            adjusted_priority += 5

        routed.append(
            {
                "id": str(ticket["id"]),
                "queue": str(queue),
                "priority": adjusted_priority,
                "status_code": "routed",
            }
        )

    return routed
