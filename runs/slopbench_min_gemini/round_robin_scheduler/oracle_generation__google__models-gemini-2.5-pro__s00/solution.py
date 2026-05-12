"""
Assigns jobs to workers using a round-robin scheduling algorithm.
"""

import itertools
from typing import Any, Dict, List


def _get_enabled_worker_names(workers: List[Dict[str, Any]]) -> List[str]:
    """
    Filters a list of worker dicts and returns the names of enabled workers.

    A worker is considered enabled if its 'enabled' key is True or absent.
    """
    return [
        worker["name"]
        for worker in workers
        if worker.get("enabled", True)
    ]


def assign_round_robin(
    workers: List[Dict[str, Any]], jobs: List[str]
) -> List[Dict[str, str]]:
    """
    Assigns jobs to a list of workers in a round-robin fashion.

    Only workers that are marked as "enabled" (or have no "enabled" field)
    will be included in the rotation. The order of workers and jobs in the
    input lists is preserved in the assignment logic.

    Args:
        workers: A list of worker dictionaries. Each must have a "name" key.
                 An optional "enabled": bool key can be used to exclude a worker.
                 "enabled" defaults to True if not present.
        jobs: A list of job identifier strings to be assigned.

    Returns:
        A list of assignment dictionaries, where each dictionary has a "job"
        key and a "worker" key, representing the assignment.

    Raises:
        ValueError: If the list of workers contains no enabled workers, as
                    no jobs can be assigned.
    """
    enabled_worker_names = _get_enabled_worker_names(workers)

    if not enabled_worker_names:
        raise ValueError("No enabled workers available to assign jobs.")

    worker_cycle = itertools.cycle(enabled_worker_names)

    assignments = [
        {"job": job, "worker": next(worker_cycle)}
        for job in jobs
    ]

    return assignments
