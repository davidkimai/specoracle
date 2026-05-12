"""
A module for assigning jobs to workers using a round-robin scheduling algorithm.
"""

import itertools
from typing import Any, Dict, List

__all__ = ["assign_round_robin"]


def _get_enabled_worker_names(workers: List[Dict[str, Any]]) -> List[str]:
    """
    Filters a list of worker dictionaries to find those that are enabled.

    An enabled worker is one where the 'enabled' key is True or is absent.

    Args:
        workers: A list of worker dictionaries.

    Returns:
        A list of names of the enabled workers, preserving their original order.

    Raises:
        ValueError: If a worker dictionary is missing the required 'name' key.
    """
    enabled_names = []
    for worker in workers:
        if not isinstance(worker, dict):
            raise TypeError("Each item in 'workers' list must be a dictionary.")

        is_enabled = worker.get("enabled", True)
        if is_enabled:
            if "name" not in worker:
                raise ValueError("Found a worker dictionary missing a 'name' key.")
            enabled_names.append(worker["name"])
    return enabled_names


def assign_round_robin(
    workers: List[Dict[str, Any]], jobs: List[str]
) -> List[Dict[str, str]]:
    """
    Assigns a list of jobs to a list of workers in a round-robin fashion.

    This function filters for workers that are "enabled". A worker is
    considered enabled if its dictionary has an "enabled" key set to True,
    or if the "enabled" key is not present.

    The assignments are returned as a list of dictionaries, each mapping a
    single job to a single worker.

    Args:
        workers: A list of worker dictionaries. Each dictionary must have a
                 'name' key (str) and may have an 'enabled' key (bool).
        jobs: A list of job identifier strings to be assigned.

    Returns:
        A list of assignment dictionaries, where each dictionary has a "job"
        key and a "worker" key.

    Raises:
        ValueError: If no workers are enabled and there are jobs to assign.
        TypeError: If 'workers' or 'jobs' are not lists.
    """
    if not isinstance(workers, list):
        raise TypeError(f"Expected 'workers' to be a list, but got {type(workers)}.")
    if not isinstance(jobs, list):
        raise TypeError(f"Expected 'jobs' to be a list, but got {type(jobs)}.")

    enabled_worker_names = _get_enabled_worker_names(workers)

    if not enabled_worker_names:
        if jobs:
            raise ValueError("No enabled workers available to assign jobs.")
        return []

    worker_cycle = itertools.cycle(enabled_worker_names)

    assignments = [
        {"job": job, "worker": next(worker_cycle)}
        for job in jobs
    ]

    return assignments
