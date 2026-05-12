"""
A module for assigning jobs to workers using a round-robin scheduling algorithm.
"""

import typing

def assign_round_robin(
    workers: typing.List[typing.Dict[str, typing.Any]],
    jobs: typing.List[str]
) -> typing.List[typing.Dict[str, str]]:
    """
    Assigns jobs to enabled workers in a round-robin fashion.

    Each worker dictionary has a "name" field and an optional "enabled" field.
    The "enabled" field defaults to True if not present. Jobs from the input
    list are assigned in order to the enabled workers in a round-robin order.

    Args:
        workers: A list of worker dictionaries.
        jobs: A list of job identifier strings.

    Returns:
        A list of assignment dictionaries, each with "job" and "worker" keys.

    Raises:
        ValueError: If no workers are enabled.
    """
    # Create a new list of names for workers that are enabled.
    # A worker is considered enabled if its "enabled" key is True or missing.
    # This does not mutate the input `workers` list.
    enabled_worker_names = [
        worker["name"] for worker in workers if worker.get("enabled", True)
    ]

    if not enabled_worker_names:
        raise ValueError("No enabled workers available to assign jobs.")

    assignments = []
    num_enabled_workers = len(enabled_worker_names)

    # Assign jobs to the enabled workers in a circular (round-robin) fashion.
    # This does not mutate the input `jobs` list.
    for i, job in enumerate(jobs):
        worker_name = enabled_worker_names[i % num_enabled_workers]
        assignments.append({"job": job, "worker": worker_name})

    return assignments
