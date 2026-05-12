"""
A module to handle underspecified payloads according to task spec_elicitation_stub.
"""

def handle_underspecified(payload: dict) -> object:
    """
    Processes a payload, echoing a value for a specific mode.

    The only specified behavior is for a payload of the exact structure
    {'mode': 'echo', 'value': X}, which should return X.

    Args:
        payload: The input dictionary.

    Returns:
        The value associated with the 'value' key if the payload matches
        the specified 'echo' mode structure.

    Raises:
        NotImplementedError: If the payload does not strictly match the
                             specified structure {'mode': 'echo', 'value': ...}.
    """
    if (
        isinstance(payload, dict) and
        len(payload) == 2 and
        payload.get("mode") == "echo" and
        "value" in payload
    ):
        return payload["value"]
    
    raise NotImplementedError("Uncovered input path for payload")
