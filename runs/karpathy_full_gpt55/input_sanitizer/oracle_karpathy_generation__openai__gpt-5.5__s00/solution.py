def sanitize_fields(fields: list[str], allowed: set[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()

    for field in fields:
        if field in seen or field not in allowed:
            continue

        if all(
            char == "_"
            or "0" <= char <= "9"
            or "A" <= char <= "Z"
            or "a" <= char <= "z"
            for char in field
        ):
            seen.add(field)
            result.append(field)

    return result
