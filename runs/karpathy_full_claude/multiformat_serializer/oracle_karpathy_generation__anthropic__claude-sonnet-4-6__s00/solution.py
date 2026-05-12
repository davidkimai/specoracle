import json
import csv
import io


def serialize_record(record: dict, format: str) -> str:
    if format == 'json':
        return json.dumps(record, sort_keys=True)
    elif format == 'csv':
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=list(record.keys()))
        writer.writeheader()
        writer.writerow(record)
        return output.getvalue()
    elif format == 'toml':
        lines = []
        for key, value in record.items():
            if isinstance(value, bool):
                lines.append(f"{key} = {str(value).lower()}")
            elif isinstance(value, (int, float)):
                lines.append(f"{key} = {value}")
            elif isinstance(value, str):
                escaped = value.replace('\\', '\\\\').replace('"', '\\"')
                lines.append(f'{key} = "{escaped}"')
        return '\n'.join(lines)
    else:
        raise ValueError(f"Unsupported format: {format}")
