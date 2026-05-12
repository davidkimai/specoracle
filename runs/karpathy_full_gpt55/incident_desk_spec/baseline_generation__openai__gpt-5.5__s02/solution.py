from __future__ import annotations

__all__ = ["route_tickets"]


def route_tickets(tickets: list[dict], rules: dict[str, dict]) -> list[dict]:
    """
    Route valid incident tickets according to service rules.

    A valid ticket contains the keys: "id", "severity", and "service".
    Tickets missing any of those keys are skipped.

    If a ticket's service has no explicit rule, rules["default"] is used.
    """
    routed: list[dict] = []

    for ticket in tickets:
        if not isinstance(ticket, dict):
            continue

        if "id" not in ticket or "severity" not in ticket or "service" not in ticket:
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
