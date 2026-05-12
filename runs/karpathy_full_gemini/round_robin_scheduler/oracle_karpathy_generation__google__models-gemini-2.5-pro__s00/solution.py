"""
A module for assigning jobs to workers using a round-robin scheduling algorithm.
"""

from typing import List, Dict, Any
import itertools


def assign_round_robin(
    workers: List[Dict[str, Any]], jobs: List[str]
) -> List[Dict[str, str]]:
    """
    Assigns jobs to a list of workers in a round-robin fashion.

    This function filters for workers that are enabled, then iterates through
    the list of jobs, assigning each one to the next available worker in a
    cyclical order.

    Args:
        workers: A list of worker dictionaries. Each dictionary must have a "name"
                 key. An optional "enabled" key (boolean) can be included. If
                 "enabled" is missing or its value is not explicitly False,
                 the worker is considered enabled.
        jobs: A list of job identifiers (strings) to be assigned.

    Returns:
        A list of assignment dictionaries, where each dictionary has a "job"
        key and a "worker" key, representing the assignment of a job to a
        worker's name.

    Raises:
        ValueError: If there are no enabled workers in the input list.
    """
    enabled_workers = [
        worker for worker in workers if worker.get("enabled", True) is True
    ]

    if not enabled_workers:
        raise ValueError("No enabled workers available for assignment.")

    assignments = []
    worker_cycle = itertools.cycle(enabled_workers)

    for job in jobs:
        worker = next(worker_cycle)
        assignments.append({"job": job, "worker": worker["name"]})

    return assignments
