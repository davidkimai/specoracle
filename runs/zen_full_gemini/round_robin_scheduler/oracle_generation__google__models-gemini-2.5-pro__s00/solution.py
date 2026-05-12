import itertools
from typing import Any, Dict, List

"""
Provides a round-robin scheduler for assigning jobs to workers.
"""


def _get_enabled_worker_names(workers: List[Dict[str, Any]]) -> List[str]:
    """
    Filters a list of worker dictionaries to find those that are enabled.

    Args:
        workers: A list of dictionaries, where each dictionary represents a
                 worker and may contain 'name' and 'enabled' keys.

    Returns:
        A list of names of the workers that are enabled. A worker is
        considered enabled if its 'enabled' key is True or not present.
    """
    enabled_names = []
    for worker in workers:
        is_enabled = worker.get("enabled", True)
        if is_enabled:
            # Assuming 'name' is a required key as per the problem description.
            # A KeyError will be raised if 'name' is missing, which is
            # appropriate for malformed input.
            enabled_names.append(worker["name"])
    return enabled_names


def assign_round_robin(
    workers: List[Dict[str, Any]], jobs: List[str]
) -> List[Dict[str, str]]:
    """
    Assigns jobs to a list of workers using a round-robin algorithm.

    This function distributes jobs one by one to enabled workers, cycling
    through the workers in their original order.

    Args:
        workers: A list of dictionaries, each representing a worker. Each worker
                 must have a "name" (str) and may have an "enabled" (bool)
                 field. If "enabled" is not present, it defaults to True.
        jobs: A list of strings, where each string is a job identifier.

    Returns:
        A list of assignment dictionaries, each with "job" and "worker" keys,
        representing the scheduled assignments.

    Raises:
        ValueError: If there are no enabled workers in the input list.
    """
    enabled_worker_names = _get_enabled_worker_names(workers)

    if not enabled_worker_names:
        raise ValueError("No enabled workers available to assign jobs.")

    assignments = []
    worker_cycle = itertools.cycle(enabled_worker_names)

    for job in jobs:
        assigned_worker = next(worker_cycle)
        assignments.append({"job": job, "worker": assigned_worker})

    return assignments
