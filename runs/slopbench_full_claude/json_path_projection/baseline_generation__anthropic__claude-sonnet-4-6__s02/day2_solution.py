def extract_fields(record: dict, paths: dict[str, str], default=None, required: set | None = None) -> dict:
    result = {}
    for output_key, path in paths.items():
        parts = path.split(".")
        current = record
        resolved = True
        for part in parts:
            if isinstance(current, dict):
                if part in current:
                    current = current[part]
                else:
                    resolved = False
                    break
            elif isinstance(current, list):
                try:
                    index = int(part)
                    current = current[index]
                except (ValueError, IndexError):
                    resolved = False
                    break
            else:
                resolved = False
                break
        if not resolved and required is not None and output_key in required:
            raise KeyError(output_key)
        result[output_key] = current if resolved else default
    return result
