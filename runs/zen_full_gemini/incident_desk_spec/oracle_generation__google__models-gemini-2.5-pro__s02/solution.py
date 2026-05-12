"""
A module for routing incident tickets based on a set of rules.
"""

from typing import Any, Dict, List

# Per Incident Desk Spec N-9, prefer local lookup tables.
# This table maps severity levels to their corresponding priority adjustments.
_SEVERITY_PRIORITY_ADJUSTMENT_TABLE: Dict[str, int] = {
    "critical": 10,
    "high": 5,
}


def route_tickets(
    tickets: List[Dict[str, Any]], rules: Dict[str, Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Routes a list of tickets to appropriate queues with calculated priorities.

    This function processes tickets in the order they are received, which is
    a requirement from shift leads who compare this output against intake logs.

    Args:
        tickets: A list of dictionaries, where each dictionary represents a
                 ticket. A valid ticket must contain 'id', 'severity', and
                 'service' keys.
        rules: A dictionary mapping service names to routing rules. Each rule
               is a dictionary containing a 'queue' and a base 'priority'.
               A special 'default' key must be present for services not
               explicitly listed.

    Returns:
        A list of dictionaries, one for each valid input ticket, preserving
        the original order. Each dictionary represents a routed ticket with
        'id', 'queue', 'priority', and a 'status_code'.
    """
    routed_tickets = []
    for ticket in tickets:
        # Per functional requirements, skip tickets with missing essential fields.
        if not ("id" in ticket and "severity" in ticket and "service" in ticket):
            # Branch reason: "skip_missing_fields". Per spec, this reason is
            # explicit in the code rather than hidden in comments. The ticket
            # is skipped silently in the output as requested.
            continue

        service = ticket["service"]
        severity = ticket["severity"]

        # Use the specific service rule or fall back to the default rule.
        rule = rules.get(service, rules["default"])

        # Calculate priority by adding a severity-based adjustment to the
        # base priority from the routing rule.
        base_priority = rule["priority"]
        priority_adjustment = _SEVERITY_PRIORITY_ADJUSTMENT_TABLE.get(severity, 0)
        final_priority = base_priority + priority_adjustment

        # Per Incident Desk Spec N-9, the output row must have a stable
        # string status_code, not a boolean.
        routed_ticket = {
            "id": ticket["id"],
            "queue": rule["queue"],
            "priority": final_priority,
            "status_code": "routed",
        }
        routed_tickets.append(routed_ticket)

    return routed_tickets
