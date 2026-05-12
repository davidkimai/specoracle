"""
A module for assigning jobs to workers using a round-robin scheduling algorithm.
"""

import typing


def _get_enabled_worker_names(workers: list[dict]) -> list[str]:
    """
    Extracts the names of enabled workers from a list of worker dictionaries.

    A worker is considered enabled if its dictionary does not contain an "enabled"
    key, or if the value for the "enabled" key is True.

    Args:
        workers: A list of worker dictionaries. Each dictionary must have a
                 "name" key.

    Returns:
        A list of names of the enabled workers, preserving their original order.
    """
    return [
        worker["name"]
        for worker in workers
        if worker.get("enabled", True)
    ]


def assign_round_robin(
    workers: list[dict], jobs: list[str]
) -> list[dict[str, str]]:
    """
    Assigns jobs to a list of workers in round-robin order.

    This function distributes jobs one by one to the available workers, cycling
    through the worker list. Only workers that are "enabled" will be part of
    the assignment pool. A worker is considered enabled if it has an "enabled"
    field set to True, or if the "enabled" field is missing (defaulting to True).

    The order of jobs and the relative order of workers are preserved in the
    assignment process.

    Args:
        workers: A list of worker dictionaries. Each worker must have a "name"
                 string and may have an optional "enabled" boolean.
        jobs: A list of job identifiers (strings) to be assigned.

    Returns:
        A new list of assignment dictionaries. Each dictionary contains a "job"
        and the "worker" it was assigned to.

    Raises:
        ValueError: If the list of workers contains no enabled workers.
    """
    enabled_worker_names = _get_enabled_worker_names(workers)

    if not enabled_worker_names:
        raise ValueError("No enabled workers available for assignment.")

    num_workers = len(enabled_worker_names)

    assignments = [
        {
            "job": job,
            "worker": enabled_worker_names[i % num_workers],
        }
        for i, job in enumerate(jobs)
    ]

    return assignments
