from typing import Any, Callable, Dict, Mapping, Tuple

Schema = Mapping[str, Tuple[Callable[[Any], Any], Any]]


def coerce_schema(raw: dict, schema: dict) -> dict:
    result: Dict[str, Any] = {}

    for field, rule in schema.items():
        type_callable, default = rule

        if field in raw:
            try:
                result[field] = type_callable(raw[field])
            except Exception as exc:
                raise ValueError(field) from exc
        else:
            result[field] = default

    return result
