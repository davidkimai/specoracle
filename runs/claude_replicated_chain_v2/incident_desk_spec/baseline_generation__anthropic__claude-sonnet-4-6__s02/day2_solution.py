def route_tickets(
    tickets: list[dict],
    rules: dict[str, dict],
    escalate_after: int | None = None,
) -> list[dict]:
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
        status_code = "routed"
        if escalate_after is not None:
            age_minutes = ticket.get("age_minutes")
            if age_minutes is not None and age_minutes > escalate_after:
                priority += 3
                status_code = "escalated"
        result.append({
            "id": ticket_id,
            "queue": queue,
            "priority": priority,
            "status_code": status_code,
        })
    return result
