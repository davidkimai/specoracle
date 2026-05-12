def sanitize_fields(fields: list[str], allowed: set[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()

    for field in fields:
        if field in seen or field not in allowed:
            continue
        if all(("a" <= char <= "z") or ("A" <= char <= "Z") or ("0" <= char <= "9") or char == "_" for char in field):
            result.append(field)
            seen.add(field)

    return result
