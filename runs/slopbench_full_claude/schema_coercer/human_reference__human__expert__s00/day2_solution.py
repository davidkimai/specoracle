from __future__ import annotations


def coerce_schema(raw: dict, schema: dict, nullable: set[str] | None = None) -> dict:
    output = {}
    nullable = nullable or set()
    for field, (caster, default) in schema.items():
        value = raw.get(field, default)
        if field in nullable and value is None:
            output[field] = None
            continue
        try:
            output[field] = caster(value)
        except Exception as exc:
            raise ValueError(f'could not coerce {field}') from exc
    return output
