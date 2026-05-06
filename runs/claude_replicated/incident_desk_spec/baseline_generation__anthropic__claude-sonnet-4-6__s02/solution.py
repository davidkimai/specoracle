def route_tickets(tickets: list[dict], rules: dict[str, dict]) -> list[dict]:
    result = []
    for ticket in tickets:
        if "id" not in ticket or "severity" not in ticket or "service" not in ticket:
            continue
        ticket_id = ticket["id"]
        severity = ticket["severity"]
        service = ticket["service"]
        rule = rules.get(service, rules.get("default", {}))
        queue = rule.get("queue", "")
        priority = rule.get("priority", 0)
        if severity == "critical":
            priority += 10
        elif severity == "high":
            priority += 5
        result.append({
            "id": ticket_id,
            "queue": queue,
            "priority": priority,
            "status_code": "routed",
        })
    return result
