from typing import Any, Mapping

_MISSING = object()


def _parse_index(segment: str) -> int | None:
    if not segment:
        return None

    start = 1 if segment[0] == "-" else 0
    if start == len(segment):
        return None

    if not segment[start:].isdigit():
        return None

    return int(segment)


def _resolve_path(record: Any, path: str) -> Any:
    current = record

    if path == "":
        return current

    for segment in path.split("."):
        if isinstance(current, Mapping):
            if segment not in current:
                return _MISSING
            current = current[segment]
        elif isinstance(current, list):
            index = _parse_index(segment)
            if index is None:
                return _MISSING
            try:
                current = current[index]
            except IndexError:
                return _MISSING
        else:
            return _MISSING

    return current


def extract_fields(record: dict, paths: dict[str, str], default=None) -> dict:
    result = {}

    for output_key, path in paths.items():
        value = _resolve_path(record, path)
        result[output_key] = default if value is _MISSING else value

    return result
