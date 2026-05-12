"""
A module for assigning jobs to workers using a round-robin scheduling algorithm.
"""

from typing import List, Dict, Any

def assign_round_robin(workers: List[Dict[str, Any]], jobs: List[str]) -> List[Dict[str, str]]:
    """
    Assigns jobs to enabled workers in a round-robin fashion.

    Each worker in the `workers` list is a dictionary that must contain a "name"
    key. It may optionally contain an "enabled" key, which defaults to True if
    not present. Jobs from the `jobs` list are assigned sequentially to the
    list of enabled workers, wrapping around when the end of the worker list
    is reached.

    Args:
        workers: A list of worker dictionaries.
                 Example: [{"name": "worker-1"}, {"name": "worker-2", "enabled": False}]
        jobs: A list of job identifier strings.
              Example: ["job-a", "job-b", "job-c"]

    Returns:
        A list of assignment dictionaries, where each dictionary maps a job to
        a worker.
        Example: [{"job": "job-a", "worker": "worker-1"},
                  {"job": "job-b", "worker": "worker-1"},
                  {"job": "job-c", "worker": "worker-1"}]
        (Assuming only worker-1 is enabled from the example above).

    Raises:
        ValueError: If the list of workers contains no enabled workers.
    """
    # Filter for enabled workers. The 'enabled' key defaults to True.
    # This creates a new list and does not mutate the input `workers`.
    enabled_worker_names = [
        worker["name"]
        for worker in workers
        if worker.get("enabled", True)
    ]

    # Raise an error if no workers are available to be assigned jobs.
    if not enabled_worker_names:
        raise ValueError("No enabled workers available.")

    assignments: List[Dict[str, str]] = []
    num_enabled_workers = len(enabled_worker_names)

    # Assign jobs to the enabled workers in round-robin order.
    for i, job in enumerate(jobs):
        # The modulo operator ensures the index wraps around the worker list.
        worker_name = enabled_worker_names[i % num_enabled_workers]
        assignments.append({"job": job, "worker": worker_name})

    return assignments
