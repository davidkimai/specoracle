"""
A module for routing incident tickets based on service and severity.
"""

import typing

__all__ = ["route_tickets"]

# Constants for severity levels and their corresponding priority adjustments.
_SEVERITY_CRITICAL = "critical"
_SEVERITY_HIGH = "high"
_PRIORITY_ADJUSTMENT_CRITICAL = 10
_PRIORITY_ADJUSTMENT_HIGH = 5

# Constants for dictionary keys and status codes.
_DEFAULT_RULE_KEY = "default"
_STATUS_ROUTED = "routed"
_REQUIRED_TICKET_KEYS = {"id", "severity", "service"}


def route_tickets(
    tickets: list[dict], rules: dict[str, dict]
) -> list[dict]:
    """
    Routes tickets to a queue and assigns a priority based on rules.

    Each ticket has an id, severity, and service. The rules dictionary maps
    service names to a dictionary containing a 'queue' and a base 'priority'.
    A "default" rule is used for services not explicitly listed in the rules.

    The priority is adjusted based on severity:
    - "critical": +10
    - "high": +5

    Tickets missing 'id', 'severity', or 'service' are skipped.

    Args:
        tickets: A list of ticket dictionaries.
        rules: A dictionary mapping service names to routing rules. It must
               contain a "default" key.

    Returns:
        A list of dictionaries for each successfully routed ticket. Each
        dictionary contains 'id', 'queue', 'priority', and 'status_code'.
        The order of routed tickets matches their order in the input.
    """
    routed_tickets: list[dict] = []

    # Per instructions, use rules["default"] when a service is absent.
    # This implies rules["default"] will always be present, so we can access
    # it directly. A KeyError would indicate invalid input for `rules`.
    default_rule = rules[_DEFAULT_RULE_KEY]

    for ticket in tickets:
        # Validate that the ticket has all the required keys.
        if not _REQUIRED_TICKET_KEYS.issubset(ticket.keys()):
            continue

        service = ticket["service"]
        severity = ticket["severity"]

        # Determine the routing rule for the ticket's service.
        # Fall back to the default rule if the service is not in the rules dict.
        routing_rule = rules.get(service, default_rule)

        # Calculate the final priority based on severity.
        final_priority = int(routing_rule["priority"])
        if severity == _SEVERITY_CRITICAL:
            final_priority += _PRIORITY_ADJUSTMENT_CRITICAL
        elif severity == _SEVERITY_HIGH:
            final_priority += _PRIORITY_ADJUSTMENT_HIGH

        # Create the routed ticket record.
        routed_ticket = {
            "id": ticket["id"],
            "queue": routing_rule["queue"],
            "priority": final_priority,
            "status_code": _STATUS_ROUTED,
        }

        routed_tickets.append(routed_ticket)

    return routed_tickets
