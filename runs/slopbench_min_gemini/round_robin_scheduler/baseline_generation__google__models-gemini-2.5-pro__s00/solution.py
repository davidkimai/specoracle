"""
A module for round-robin job scheduling.
"""

from itertools import cycle
from typing import Any, Dict, List


def assign_round_robin(
    workers: List[Dict[str, Any]], jobs: List[str]
) -> List[Dict[str, str]]:
    """
    Assigns jobs to enabled workers in a round-robin fashion.

    Each worker in the `workers` list is a dictionary that must contain a "name"
    key. It may also contain an "enabled" key with a boolean value. If the
    "enabled" key is missing, the worker is considered enabled by default.

    The function assigns jobs from the `jobs` list to the enabled workers in
    the order they appear in their respective lists, cycling through the
    enabled workers.

    Args:
        workers: A list of worker dictionaries.
        jobs: A list of job identifier strings.

    Returns:
        A list of assignment dictionaries, where each dictionary has a "job"
        key (the job identifier) and a "worker" key (the name of the assigned
        worker).

    Raises:
        ValueError: If there are no enabled workers in the input list.
    """
    # Create a new list of names for workers that are enabled.
    # A worker is enabled if its "enabled" key is True or not present.
    # This approach does not mutate the input `workers` list.
    enabled_worker_names = [
        worker["name"]
        for worker in workers
        if worker.get("enabled", True)
    ]

    # If there are no workers to assign jobs to, it's an invalid state.
    if not enabled_worker_names:
        raise ValueError("No enabled workers available for assignment.")

    # Create an infinite iterator that cycles through the enabled workers.
    worker_cycle = cycle(enabled_worker_names)

    # Build the list of assignments by pairing each job with the next worker
    # from the cycle.
    assignments = [
        {"job": job, "worker": next(worker_cycle)}
        for job in jobs
    ]

    return assignments
