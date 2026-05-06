from __future__ import annotations


def handle_underspecified(payload: dict):
    if payload.get('mode') == 'echo' and 'value' in payload:
        return payload['value']
    if payload.get('mode') == 'count' and 'items' in payload:
        return len(payload['items'])
    raise NotImplementedError('uncovered input path')
