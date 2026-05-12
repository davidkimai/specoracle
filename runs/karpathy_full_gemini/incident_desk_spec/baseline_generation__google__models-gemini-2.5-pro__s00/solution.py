import collections.abc

# Module-level constants for keys and severity adjustments
_REQUIRED_TICKET_KEYS: set[str] = {"id", "severity", "service"}
_CRITICAL_SEVERITY: str = "critical"
_HIGH_SEVERITY: str = "high"
_CRITICAL_PRIORITY_BOOST: int = 10
_HIGH_PRIORITY_BOOST: int = 5
_DEFAULT_RULE_KEY: str = "default"


def route_tickets(
    tickets: list[dict], rules: dict[str, dict]
) -> list[dict]:
    """
    Routes a list of tickets to appropriate queues with calculated priorities.

    Each ticket is validated to ensure it contains 'id', 'severity', and 'service'.
    A routing rule is selected based on the ticket's service, with a fallback
    to a "default" rule if the specific service is not found in the ruleset.
    The ticket's priority is adjusted based on its severity.

    Args:
        tickets: A list of dictionaries, where each represents a ticket.
        rules: A dictionary mapping service names to routing rules. A special
               "default" key provides a fallback for unknown services.

    Returns:
        A list of dictionaries for each valid ticket, containing the routing
        information. The order of tickets is preserved from the input.
    """
    routed_list: list[dict] = []
    default_rule = rules.get(_DEFAULT_RULE_KEY)

    for ticket in tickets:
        if not _REQUIRED_TICKET_KEYS.issubset(ticket.keys()):
            continue

        service = ticket["service"]
        rule = rules.get(service, default_rule)

        if not isinstance(rule, collections.abc.Mapping) or "queue" not in rule or "priority" not in rule:
            continue

        base_priority = rule["priority"]
        severity = ticket["severity"]

        final_priority = base_priority
        if severity == _CRITICAL_SEVERITY:
            final_priority += _CRITICAL_PRIORITY_BOOST
        elif severity == _HIGH_SEVERITY:
            final_priority += _HIGH_PRIORITY_BOOST

        routed_list.append({
            "id": ticket["id"],
            "queue": rule["queue"],
            "priority": final_priority,
            "status_code": "routed",
        })

    return routed_list
