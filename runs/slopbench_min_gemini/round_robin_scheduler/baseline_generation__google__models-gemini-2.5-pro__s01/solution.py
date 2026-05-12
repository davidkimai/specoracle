"""
A module for scheduling jobs to workers using a round-robin algorithm.
"""

import typing

def assign_round_robin(
    workers: list[dict[str, typing.Any]],
    jobs: list[str]
) -> list[dict[str, str]]:
    """Assigns jobs to enabled workers in a round-robin fashion.

    Each worker in the `workers` list is a dictionary that must have a "name"
    key. It can also have an optional "enabled" key. If "enabled" is not
    present, it defaults to True. Workers with "enabled" set to False are
    skipped.

    The function assigns jobs from the `jobs` list to the enabled workers
    sequentially. When the end of the worker list is reached, it wraps around
    to the beginning.

    Args:
        workers: A list of worker dictionaries. Each dictionary must have a
                 "name" key and may have an "enabled" boolean key.
        jobs: A list of job identifiers (strings) to be assigned.

    Returns:
        A list of assignment dictionaries, where each dictionary has a "job"
        key and a "worker" key, representing the assignment of a job to a
        worker's name.

    Raises:
        ValueError: If the list of workers contains no enabled workers.
    """
    # Filter for enabled workers, defaulting 'enabled' to True if not present.
    # This creates a new list of worker names and does not mutate the input.
    enabled_worker_names = [
        worker["name"] for worker in workers if worker.get("enabled", True)
    ]

    # Raise an error if no workers are available for assignment.
    if not enabled_worker_names:
        raise ValueError("No enabled workers available for assignment.")

    num_enabled_workers = len(enabled_worker_names)
    assignments = []

    # Assign jobs in a round-robin manner using the modulo operator.
    for i, job in enumerate(jobs):
        worker_name = enabled_worker_names[i % num_enabled_workers]
        assignments.append({"job": job, "worker": worker_name})

    return assignments
