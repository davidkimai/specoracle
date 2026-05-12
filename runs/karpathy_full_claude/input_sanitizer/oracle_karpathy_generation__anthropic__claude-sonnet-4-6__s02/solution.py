import re

def sanitize_fields(fields: list[str], allowed: set[str]) -> list[str]:
    seen = set()
    result = []
    for field in fields:
        if field in allowed and re.fullmatch(r'[A-Za-z0-9_]+', field) and field not in seen:
            seen.add(field)
            result.append(field)
    return result
