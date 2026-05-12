_ECHO_KEYS = {"mode", "value"}


def _is_echo_payload(payload: object) -> bool:
    if not isinstance(payload, dict):
        return False

    if set(payload) != _ECHO_KEYS:
        return False

    return payload["mode"] == "echo"


def handle_underspecified(payload: dict) -> object:
    if _is_echo_payload(payload):
        return payload["value"]

    raise NotImplementedError(
        "Only the exact payload shape {'mode': 'echo', 'value': X} is specified."
    )
