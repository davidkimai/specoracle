from typing import Any


def route_tickets(tickets: list[dict], rules: dict[str, dict]) -> list[dict]:
    """
    Route valid tickets according to service routing rules.

    A valid ticket contains the keys "id", "severity", and "service".
    Tickets missing any of those keys are skipped.

    If a ticket's service is not present in rules, rules["default"] is used.
    """
    routed: list[dict] = []
    default_rule = rules.get("default")

    for ticket in tickets:
        if not isinstance(ticket, dict):
            continue

        if "id" not in ticket or "severity" not in ticket or "service" not in ticket:
            continue

        service = ticket["service"]
        rule: Any = rules.get(service, default_rule)

        if not isinstance(rule, dict):
            continue

        if "queue" not in rule or "priority" not in rule:
            continue

        try:
            priority = int(rule["priority"])
        except (TypeError, ValueError):
            continue

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
