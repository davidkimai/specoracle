"""
A module for round-robin job scheduling.
"""

from typing import List, Dict, Any, Sequence

def assign_round_robin(
    workers: Sequence[Dict[str, Any]],
    jobs: Sequence[str]
) -> List[Dict[str, str]]:
    """
    Assigns jobs to a list of workers using a round-robin scheduling algorithm.

    Each worker in the `workers` list is a dictionary that must contain a "name"
    key. It may also contain an "enabled" key with a boolean value. If "enabled"
    is missing, it defaults to True.

    Jobs from the `jobs` list are assigned sequentially to the enabled workers
    in a circular order.

    Args:
        workers: A sequence of worker dictionaries.
        jobs: A sequence of job identifiers to be assigned.

    Returns:
        A list of assignment dictionaries, where each dictionary has a "job"
        key and a "worker" key, representing the assignment of a job to a
        worker's name.

    Raises:
        ValueError: If there are no enabled workers in the input list.
        KeyError: If a worker dictionary is missing the "name" key.
    """
    enabled_workers = [
        worker["name"] for worker in workers if worker.get("enabled", True)
    ]

    if not enabled_workers:
        raise ValueError("No enabled workers available for assignment.")

    assignments = []
    num_enabled_workers = len(enabled_workers)

    for i, job in enumerate(jobs):
        worker_name = enabled_workers[i % num_enabled_workers]
        assignments.append({"job": job, "worker": worker_name})

    return assignments
