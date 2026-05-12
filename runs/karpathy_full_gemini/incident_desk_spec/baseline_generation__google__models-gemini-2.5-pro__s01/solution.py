"""
A secure program synthesis module for routing incident tickets.

This module provides functionality to route tickets based on a set of
configurable rules, adjusting priority based on severity.
"""

# Constants for priority adjustments, status codes, and required ticket fields.
# Using constants improves readability and maintainability.
_CRITICAL_SEVERITY_BOOST = 10
_HIGH_SEVERITY_BOOST = 5
_ROUTED_STATUS = "routed"
_REQUIRED_TICKET_KEYS = ("id", "severity", "service")


def route_tickets(tickets: list[dict], rules: dict[str, dict]) -> list[dict]:
    """
    Routes a list of tickets based on a given set of rules.

    Each ticket is processed to determine its queue and priority. The priority
    is adjusted based on the ticket's severity. Tickets that are missing
    required fields ('id', 'severity', 'service') are skipped.

    Args:
        tickets: A list of dictionaries, where each dictionary represents a
                 ticket. A valid ticket must contain 'id', 'severity',
                 and 'service' keys.
        rules: A dictionary mapping service names to routing rules. Each rule
               is a dictionary with 'queue' and 'priority'. A special "default"
               key must be present to handle tickets for services not
               explicitly listed.

    Returns:
        A list of dictionaries, one for each valid ticket that was
        successfully routed. Each dictionary contains the ticket 'id',
        the assigned 'queue', the calculated 'priority', and a
        'status_code' of "routed". The order of routed tickets matches
        their order in the input list.

    Raises:
        KeyError: If the 'default' key is missing from the rules dictionary,
                  or if a rule is missing 'queue' or 'priority' keys.
                  This indicates a malformed `rules` input.
    """
    routed_tickets = []
    # Per the functional requirements, a "default" rule is guaranteed to exist.
    # Accessing it directly ensures the program fails fast with a clear
    # KeyError if this assumption is violated.
    default_rule = rules["default"]

    for ticket in tickets:
        # Validate that the ticket has all the required fields.
        # This prevents KeyErrors when accessing ticket data.
        if not all(key in ticket for key in _REQUIRED_TICKET_KEYS):
            continue

        # Get ticket data now that we know the keys exist.
        ticket_id = ticket["id"]
        severity = ticket["severity"]
        service = ticket["service"]

        # Determine the routing rule for the ticket's service.
        # Fall back to the default rule if the service is not in the rules dict.
        rule = rules.get(service, default_rule)

        # Per the requirements, a rule dictionary contains 'queue' and 'priority'.
        # Direct access will raise a KeyError for malformed rules.
        base_priority = rule["priority"]
        queue = rule["queue"]

        # Calculate the final priority based on severity.
        priority_adjustment = 0
        if severity == "critical":
            priority_adjustment = _CRITICAL_SEVERITY_BOOST
        elif severity == "high":
            priority_adjustment = _HIGH_SEVERITY_BOOST

        final_priority = base_priority + priority_adjustment

        # Construct the result for the routed ticket.
        routed_ticket_data = {
            "id": ticket_id,
            "queue": queue,
            "priority": final_priority,
            "status_code": _ROUTED_STATUS,
        }
        routed_tickets.append(routed_ticket_data)

    return routed_tickets
