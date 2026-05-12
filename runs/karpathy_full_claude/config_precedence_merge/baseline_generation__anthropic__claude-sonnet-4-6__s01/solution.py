"""
config_precedence_merge.py

Implements merge_settings with precedence: defaults < file_config < env vars.
"""

from __future__ import annotations

import copy
from typing import Any


def _parse_value(raw: str) -> Any:
    """Parse a string value into bool, int, list, or str."""
    stripped = raw.strip()

    # Boolean
    if stripped.lower() == "true":
        return True
    if stripped.lower() == "false":
        return False

    # Integer (base-10)
    try:
        return int(stripped, 10)
    except ValueError:
        pass

    # Comma-separated list (only if a comma is present)
    if "," in stripped:
        parts = [p.strip() for p in stripped.split(",")]
        parts = [p for p in parts if p]  # remove empty strings
        return parts

    # Plain string
    return stripped


def _deep_merge(base: dict, override: dict) -> dict:
    """
    Deep-merge *override* into *base*, returning a new dict.
    Neither input is mutated.
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
    Convert APP__-prefixed environment variables into a nested dict.

    APP__FOO__BAR=1  ->  {"foo": {"bar": 1}}
    """
    result: dict = {}
    prefix = "APP__"

    for key, raw_value in env.items():
        if not key.startswith(prefix):
            continue

        remainder = key[len(prefix):]
        segments = [seg.lower() for seg in remainder.split("__")]

        # Filter out empty segments that could arise from leading/trailing/double __
        segments = [seg for seg in segments if seg]
        if not segments:
            continue

        parsed = _parse_value(raw_value)

        # Build nested dict from segments
        node = result
        for seg in segments[:-1]:
            if seg not in node or not isinstance(node[seg], dict):
                node[seg] = {}
            node = node[seg]
        node[segments[-1]] = parsed

    return result


def merge_settings(defaults: dict, file_config: dict, env: dict[str, str]) -> dict:
    """
    Merge settings with precedence: defaults < file_config < environment variables.

    Parameters
    ----------
    defaults : dict
        Base default settings (lowest precedence).
    file_config : dict
        Settings loaded from a configuration file.
    env : dict[str, str]
        Environment variables mapping; only keys starting with APP__ are used.

    Returns
    -------
    dict
        A new nested settings dictionary. Input dicts are never mutated.
    """
    # Start with defaults, deep-merge file_config on top
    merged = _deep_merge(defaults, file_config)

    # Parse env vars into nested dict and deep-merge on top
    env_nested = _env_to_nested(env)
    merged = _deep_merge(merged, env_nested)

    return merged
