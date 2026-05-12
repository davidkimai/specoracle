__all__ = ["handle_underspecified"]


_ECHO_KEYS = {"mode", "value"}


def _is_specified_echo_payload(payload: object) -> bool:
    return (
        isinstance(payload, dict)
        and set(payload.keys()) == _ECHO_KEYS
        and payload["mode"] == "echo"
    )


def handle_underspecified(payload: dict) -> object:
    if _is_specified_echo_payload(payload):
        return payload["value"]

    raise NotImplementedError(
        "Unspecified payload path. The only implemented payload is exactly "
        "{'mode': 'echo', 'value': X}."
    )
