"""
A simple, stateless round-robin scheduler.
"""

import itertools


def _get_enabled_worker_names(workers: list[dict]) -> list[str]:
    """
    Filters a list of worker dicts, returning the names of enabled workers.

    A worker is considered enabled if its "enabled" key is True or if the
    key is not present.

    Args:
        workers: A list of dictionaries, where each dictionary represents a
                 worker and must contain a "name" key.

    Returns:
        A list of worker names that are available for assignment.
    """
    enabled_names = []
    for worker in workers:
        is_enabled = worker.get("enabled", True)
        if is_enabled:
            # Assuming "name" key exists as per functional requirements.
            # A KeyError will be raised if a worker dict is malformed,
            # which is desirable over silent failure.
            enabled_names.append(worker["name"])
    return enabled_names


def assign_round_robin(workers: list[dict], jobs: list[str]) -> list[dict]:
    """
    Assigns jobs to a list of workers in a round-robin fashion.

    This function iterates through the list of jobs and assigns each one to the
    next available worker in a cycle. Only workers marked as "enabled" (or
    without an "enabled" key) are considered for assignment.

    The order of workers and jobs in the input lists is preserved. This
    function does not mutate its inputs.

    Args:
        workers: A list of worker dictionaries. Each worker must have a "name"
                 string and may have an optional "enabled" boolean.
        jobs: A list of job identifiers to be assigned.

    Returns:
        A list of assignment dictionaries, each with "job" and "worker" keys.

    Raises:
        ValueError: If there are no enabled workers in the input list.
    """
    enabled_worker_names = _get_enabled_worker_names(workers)

    if not enabled_worker_names:
        raise ValueError("No enabled workers available for job assignment.")

    worker_cycle = itertools.cycle(enabled_worker_names)

    assignments = [
        {"job": job, "worker": worker_name}
        for job, worker_name in zip(jobs, worker_cycle)
    ]

    return assignments
