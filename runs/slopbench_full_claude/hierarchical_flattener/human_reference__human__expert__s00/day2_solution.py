from __future__ import annotations


def flatten_paths(value: dict, array_mode: str = 'leaf') -> dict[str, object]:
    output = {}

    def visit(prefix: str, item) -> None:
        if isinstance(item, dict):
            for key, child in item.items():
                visit(f'{prefix}.{key}' if prefix else str(key), child)
        elif isinstance(item, list) and array_mode == 'index':
            for i, child in enumerate(item):
                visit(f'{prefix}[{i}]', child)
        else:
            output[prefix] = item

    visit('', value)
    return output
