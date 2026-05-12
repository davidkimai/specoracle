"""
A module for routing incident tickets based on service and severity.
"""

# This module uses built-in generics (e.g., list[dict]) available in Python 3.9+.

# Constants for dictionary keys and values to avoid magic strings and typos.
_ID = "id"
_SEVERITY = "severity"
_SERVICE = "service"
_QUEUE = "queue"
_PRIORITY = "priority"
_STATUS_CODE = "status_code"

_REQUIRED_TICKET_KEYS = (_ID, _SEVERITY, _SERVICE)

_SEVERITY_CRITICAL = "critical"
_SEVERITY_HIGH = "high"

_PRIORITY_ADJUSTMENT_MAP = {
    _SEVERITY_CRITICAL: 10,
    _SEVERITY_HIGH: 5,
}

_DEFAULT_RULE_KEY = "default"
_STATUS_ROUTED = "routed"


def route_tickets(tickets: list[dict], rules: dict[str, dict]) -> list[dict]:
    """
    Routes tickets to a queue with a specific priority based on rules.

    Each ticket has an id, severity, and service. Rules map service names to a
    dict with queue and priority. A "default" rule is used for unknown services.
    Tickets missing id, severity, or service are skipped.
    Priority is adjusted based on severity: +10 for "critical", +5 for "high".

    Args:
        tickets: A list of ticket dictionaries.
        rules: A dictionary of routing rules, including a "default" rule.

    Returns:
        A list of dictionaries for each successfully routed ticket, preserving
        the relative order of valid tickets from the input.
    """
    routed_tickets = []
    default_rule = rules[_DEFAULT_RULE_KEY]

    for ticket in tickets:
        # Skip tickets that are missing any of the required fields.
        if not all(key in ticket for key in _REQUIRED_TICKET_KEYS):
            continue

        # Determine the routing rule, falling back to the default rule.
        service = ticket[_SERVICE]
        rule = rules.get(service, default_rule)

        # Calculate the final priority by adding a severity-based adjustment.
        base_priority = rule[_PRIORITY]
        severity = ticket[_SEVERITY]
        priority_adjustment = _PRIORITY_ADJUSTMENT_MAP.get(severity, 0)
        final_priority = base_priority + priority_adjustment

        # Build the result dictionary for the routed ticket.
        routed_tickets.append({
            _ID: ticket[_ID],
            _QUEUE: rule[_QUEUE],
            _PRIORITY: final_priority,
            _STATUS_CODE: _STATUS_ROUTED,
        })

    return routed_tickets
