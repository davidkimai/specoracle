"""
A module for extracting data from nested dictionaries using dot-separated paths.
"""

from typing import Any, Dict


def extract_fields(record: dict, paths: Dict[str, str], default: Any = None) -> Dict[str, Any]:
    """
    Extracts values from a nested dictionary based on dot-separated paths.

    Each path in the `paths` dictionary specifies a sequence of keys and list
    indexes to navigate through the `record`.

    Args:
        record: The dictionary from which to extract data.
        paths: A dictionary mapping output keys to dot-separated path strings.
               For example, {"user_name": "user.name", "order_total": "orders.0.total"}.
        default: The value to use for a path that cannot be resolved.

    Returns:
        A dictionary containing the extracted values, with keys from `paths`.
        If a path is invalid, the corresponding value will be `default`.
    """
    result = {}
    for output_key, path in paths.items():
        current_value = record
        parts = path.split('.')

        for part in parts:
            if isinstance(current_value, dict):
                try:
                    current_value = current_value[part]
                except KeyError:
                    result[output_key] = default
                    break
            elif isinstance(current_value, list):
                try:
                    index = int(part)
                    current_value = current_value[index]
                except (ValueError, IndexError):
                    result[output_key] = default
                    break
            else:
                # The path continues, but the current value is not a container.
                result[output_key] = default
                break
        else:
            # This block executes if the inner loop completed without a `break`.
            result[output_key] = current_value

    return result
