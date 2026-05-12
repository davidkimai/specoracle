"""A module for assigning jobs to workers using a round-robin scheduling algorithm."""

import itertools
from typing import Any, Dict, List

def _get_enabled_workers(workers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filters a list of worker dictionaries, returning only the enabled ones.

    A worker is considered enabled if its "enabled" field is True or if the
    field is not present.

    Args:
        workers: A list of worker dictionaries.

    Returns:
        A new list containing only the enabled worker dictionaries.
    """
    return [
        worker for worker in workers if worker.get("enabled", True)
    ]


def assign_round_robin(
    workers: List[Dict[str, Any]],
    jobs: List[str]
) -> List[Dict[str, str]]:
    """
    Assigns jobs to a list of workers in a round-robin fashion.

    Jobs are assigned in their original order to the enabled workers. The
    list of enabled workers is cycled through repeatedly until all jobs are
    assigned.

    Args:
        workers: A list of worker dictionaries. Each dictionary must have a
                 "name" key. An optional "enabled" boolean key can be
                 present; if absent, it defaults to True.
        jobs: A list of job identifier strings to be assigned.

    Returns:
        A list of assignment dictionaries, where each dictionary has a "job"
        key and a "worker" key, representing the assignment.

    Raises:
        ValueError: If the list of workers contains no enabled workers.
    """
    enabled_workers = _get_enabled_workers(workers)

    if not enabled_workers:
        raise ValueError("Cannot assign jobs: no enabled workers are available.")

    worker_cycle = itertools.cycle(enabled_workers)
    assignments = []

    for job in jobs:
        assigned_worker = next(worker_cycle)
        assignments.append({
            "job": job,
            "worker": assigned_worker["name"],
        })

    return assignments
