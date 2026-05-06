from __future__ import annotations

import json


def serialize_record(record: dict, format: str, schema_version: str | None = None) -> str:
    if schema_version is not None:
        # Prepend schema_version as the first field
        effective = {"schema_version": schema_version, **record}
    else:
        effective = record

    if format == 'json':
        return json.dumps(effective, sort_keys=True)
    if format == 'csv':
        keys = list(effective)
        return ','.join(keys) + '\n' + ','.join(str(effective[key]) for key in keys)
    if format == 'toml':
        lines = []
        for key, value in effective.items():
            rendered = json.dumps(value) if isinstance(value, str) else str(value)
            lines.append(f'{key} = {rendered}')
        return '\n'.join(lines)
    raise ValueError('unsupported format')
