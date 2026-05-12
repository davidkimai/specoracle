from typing import Any


def route_tickets(tickets: list[dict], rules: dict[str, dict]) -> list[dict]:
    routed: list[dict[str, Any]] = []

    for ticket in tickets:
        if not all(field in ticket for field in ("id", "severity", "service")):
            continue

        service = ticket["service"]
        rule = rules.get(service, rules["default"])

        priority = int(rule["priority"])
        severity = ticket["severity"]

        if severity == "critical":
            priority += 10
        elif severity == "high":
            priority += 5

        routed.append(
            {
                "id": str(ticket["id"]),
                "queue": str(rule["queue"]),
                "priority": priority,
                "status_code": "routed",
            }
        )

    return routed
