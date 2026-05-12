"""
config_precedence_merge.py

Implements merge_settings(defaults, file_config, env) with precedence:
    defaults < file_config < environment variables (APP__*)
"""

from __future__ import annotations

import copy
from typing import Any


def _parse_value(raw: str) -> Any:
    """Parse a raw string value into the appropriate Python type."""
    stripped = raw.strip()

    # Boolean check (case-insensitive)
    if stripped.lower() == "true":
        return True
    if stripped.lower() == "false":
        return False

    # Integer check (base-10)
    try:
        return int(stripped, 10)
    except ValueError:
        pass

    # Comma-separated list check
    if "," in stripped:
        parts = [p.strip() for p in stripped.split(",")]
        parts = [p for p in parts if p]  # remove empty strings
        return parts

    # Default: plain string
    return stripped


def _deep_merge(base: dict, override: dict) -> dict:
    """
    Recursively merge override into base, returning a new dict.
    Neither base nor override is mutated.
    """
    result = copy.deepcopy(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def _env_to_nested(env: dict[str, str]) -> dict:
    """
    Convert APP__* environment variables into a nested dictionary.
    Keys starting with APP__ are split on __ (after stripping the prefix),
    each segment is lowercased, and the value is parsed.
    """
    nested: dict = {}

    for key, raw_value in env.items():
        if not key.startswith("APP__"):
            continue

        # Remove the APP__ prefix and split on __
        remainder = key[len("APP__"):]
        segments = remainder.split("__")

        # Lowercase each segment
        segments = [seg.lower() for seg in segments]

        # Skip if any segment is empty (e.g. APP____FOO)
        if any(seg == "" for seg in segments):
            continue

        parsed_value = _parse_value(raw_value)

        # Navigate / create the nested structure
        current = nested
        for seg in segments[:-1]:
            if seg not in current or not isinstance(current[seg], dict):
                current[seg] = {}
            current = current[seg]

        last_seg = segments[-1]
        # If the existing value is a dict and the new value is also a dict, merge;
        # otherwise, simply set.
        if last_seg in current and isinstance(current[last_seg], dict) and isinstance(parsed_value, dict):
            current[last_seg] = _deep_merge(current[last_seg], parsed_value)
        else:
            current[last_seg] = parsed_value

    return nested


def merge_settings(defaults: dict, file_config: dict, env: dict[str, str]) -> dict:
    """
    Merge settings from three sources with the following precedence
    (highest wins): environment variables > file_config > defaults.

    Parameters
    ----------
    defaults : dict
        Base/default configuration values.
    file_config : dict
        Configuration loaded from a file (e.g. YAML/TOML/JSON).
    env : dict[str, str]
        Environment variables; only keys starting with APP__ are considered.

    Returns
    -------
    dict
        A new nested dictionary with all sources merged.
    """
    # Start with defaults, then merge file_config on top
    merged = _deep_merge(defaults, file_config)

    # Convert env vars to nested dict and merge on top
    env_nested = _env_to_nested(env)
    merged = _deep_merge(merged, env_nested)

    return merged
