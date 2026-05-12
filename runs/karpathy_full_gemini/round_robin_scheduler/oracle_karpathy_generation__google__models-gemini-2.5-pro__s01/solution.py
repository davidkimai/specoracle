"""
A module for assigning jobs to workers using a round-robin scheduling algorithm.
"""

from typing import Dict, List, Any


def assign_round_robin(workers: List[Dict[str, Any]], jobs: List[str]) -> List[Dict[str, str]]:
    """
    Assigns jobs to enabled workers in a round-robin fashion.

    Workers are represented by dictionaries, which must contain a "name" key.
    They may also contain an "enabled" key (boolean). If the "enabled" key is
    absent, the worker is considered enabled by default.

    The assignment respects the input order of both jobs and workers.

    Args:
        workers: A list of worker dictionaries.
        jobs: A list of job identifier strings.

    Returns:
        A list of assignment dictionaries, where each dictionary has a "job"
        key and a "worker" key, representing the assignment.

    Raises:
        ValueError: If there are no enabled workers in the input list.
    """
    # Filter for enabled workers, preserving their original order.
    # A worker is considered enabled if the "enabled" key is True or absent.
    enabled_worker_names = [
        worker["name"] for worker in workers if worker.get("enabled", True)
    ]

    # Raise an error if no workers are available to take jobs.
    if not enabled_worker_names:
        raise ValueError("No enabled workers available to assign jobs.")

    # Assign jobs to the enabled workers in a round-robin sequence.
    assignments = []
    num_enabled_workers = len(enabled_worker_names)
    for i, job in enumerate(jobs):
        # Use the modulo operator to cycle through the list of workers.
        worker_name = enabled_worker_names[i % num_enabled_workers]
        assignments.append({"job": job, "worker": worker_name})

    return assignments
