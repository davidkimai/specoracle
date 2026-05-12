from typing import Any


def assign_round_robin(workers: list[dict[str, Any]], jobs: list[str]) -> list[dict[str, str]]:
    """
    Assign jobs to enabled workers in round-robin order.

    Each worker dictionary must contain a "name" field. The "enabled" field is
    optional and defaults to True. Inputs are not mutated.

    Raises:
        ValueError: If there are no enabled workers.
    """
    enabled_worker_names = [
        worker["name"]
        for worker in workers
        if worker.get("enabled", True)
    ]

    if not enabled_worker_names:
        raise ValueError("no enabled workers")

    worker_count = len(enabled_worker_names)
    return [
        {"job": job, "worker": enabled_worker_names[index % worker_count]}
        for index, job in enumerate(jobs)
    ]
