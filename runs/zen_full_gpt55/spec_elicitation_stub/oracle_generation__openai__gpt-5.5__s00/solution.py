from typing import Any

__all__ = ["handle_underspecified"]

_ECHO_PAYLOAD_KEYS = frozenset({"mode", "value"})


def _is_echo_payload(payload: dict[str, Any]) -> bool:
    return set(payload) == _ECHO_PAYLOAD_KEYS and payload["mode"] == "echo"


def handle_underspecified(payload: dict) -> object:
    if not isinstance(payload, dict):
        raise NotImplementedError(
            "Only payloads shaped exactly as {'mode': 'echo', 'value': X} "
            "are implemented."
        )

    if _is_echo_payload(payload):
        return payload["value"]

    raise NotImplementedError(
        "Only payloads shaped exactly as {'mode': 'echo', 'value': X} "
        "are implemented."
    )
