"""
A module for assigning jobs to workers using a round-robin scheduling algorithm.
"""

from typing import List, Dict, Any

def assign_round_robin(
    workers: List[Dict[str, Any]], jobs: List[str]
) -> List[Dict[str, str]]:
    """
    Assigns jobs to enabled workers in a round-robin fashion.

    Each worker in the `workers` list is a dictionary that must have a "name" key.
    It may also have an "enabled" key, which defaults to True if not present.
    Only workers that are "enabled" will be considered for job assignment.

    Args:
        workers: A list of worker dictionaries. Each dictionary must have a
                 "name" and may have an "enabled" status.
        jobs: A list of job identifiers (strings) to be assigned.

    Returns:
        A list of assignment dictionaries, where each dictionary has a "job"
        and a "worker" key, representing the assignment of a job to a worker.

    Raises:
        ValueError: If there are no enabled workers in the `workers` list.
    """
    # Filter for workers that are enabled. A worker is enabled if its 'enabled'
    # key is True or if the key is not present. This creates a new list and
    # does not mutate the input.
    enabled_worker_names = [
        worker["name"]
        for worker in workers
        if worker.get("enabled", True)
    ]

    # If there are no enabled workers, we cannot assign any jobs.
    if not enabled_worker_names:
        raise ValueError("No enabled workers available for assignment.")

    assignments = []
    num_enabled_workers = len(enabled_worker_names)

    # Iterate through the jobs and assign them to workers in a round-robin manner.
    for i, job in enumerate(jobs):
        # The modulo operator ensures we cycle through the worker list.
        worker_name = enabled_worker_names[i % num_enabled_workers]
        assignments.append({"job": job, "worker": worker_name})

    return assignments
