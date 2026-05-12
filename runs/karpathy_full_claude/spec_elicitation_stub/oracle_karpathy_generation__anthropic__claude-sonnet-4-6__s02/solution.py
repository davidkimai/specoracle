def handle_underspecified(payload: dict) -> object:
    if payload.get('mode') == 'echo' and 'value' in payload:
        return payload['value']
    raise NotImplementedError(f"Unhandled payload: {payload!r}")
