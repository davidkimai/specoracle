"""
A secure and correct implementation of a round-robin scheduler.
"""

from typing import Any, Dict, List

__all__ = ["assign_round_robin"]


def assign_round_robin(
    workers: List[Dict[str, Any]], jobs: List[str]
) -> List[Dict[str, str]]:
    """Assigns jobs to workers in a round-robin fashion.

    Each worker dictionary must have a "name" key. An optional "enabled" key
    (boolean) can be provided. If "enabled" is missing or set to True, the
    worker is considered available for job assignment.

    This function does not mutate the input lists.

    Args:
        workers: A list of worker dictionaries.
                 Example: [{"name": "w1", "enabled": True}, {"name": "w2"}]
        jobs: A list of job identifier strings to be assigned.
              Example: ["job1", "job2", "job3"]

    Returns:
        A list of assignment dictionaries, where each dictionary maps a job
        to a worker's name.
        Example: [{"job": "job1", "worker": "w1"},
                  {"job": "job2", "worker": "w2"},
                  {"job": "job3", "worker": "w1"}]

    Raises:
        ValueError: If there are no enabled workers in the input list.
    """
    # Filter for workers that are explicitly enabled or have no "enabled" key.
    # This creates a new list and does not mutate the original `workers` input.
    enabled_workers = [
        worker for worker in workers if worker.get("enabled", True)
    ]

    if not enabled_workers:
        raise ValueError("No enabled workers available for assignment.")

    assignments = []
    num_enabled_workers = len(enabled_workers)

    # Iterate through jobs and assign to enabled workers in a circular manner
    # using the modulo operator.
    for i, job in enumerate(jobs):
        worker_for_job = enabled_workers[i % num_enabled_workers]
        assignments.append({
            "job": job,
            "worker": worker_for_job["name"],
        })

    return assignments
