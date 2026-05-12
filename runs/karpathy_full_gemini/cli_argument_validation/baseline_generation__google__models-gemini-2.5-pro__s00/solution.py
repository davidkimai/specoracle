"""
A module for parsing and validating command-line arguments.
"""

from typing import Any, Dict, List


def parse_cli_args(argv: List[str]) -> Dict[str, Any]:
    """
    Parses and validates command-line arguments.

    Supported flags:
    - --input PATH: Required. A path to the input file.
    - --limit N: Optional, defaults to 100. Must be a positive integer.
    - --format VALUE: Optional, defaults to "json". Must be "json" or "csv".
    - --dry-run: Optional boolean flag.

    Args:
        argv: A list of strings representing the command-line arguments,
              typically sys.argv[1:].

    Returns:
        A dictionary containing the parsed arguments:
        {"input": str, "limit": int, "format": str, "dry_run": bool}.

    Raises:
        ValueError: For any of the following conditions:
                    - A required flag is missing.
                    - An unknown flag is provided.
                    - A flag that requires a value is missing its value.
                    - A flag is given an invalid
