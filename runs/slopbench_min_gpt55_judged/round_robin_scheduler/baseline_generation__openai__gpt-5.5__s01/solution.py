from __future__ import annotations


def assign_round_robin(workers: list[dict], jobs: list[str]) -> list[dict]:
    """
    Assign jobs to enabled workers in round-robin order.

    Each worker is expected to have a "name" field and may have an "enabled"
    field. Workers without an "enabled" field are treated as enabled.

    Args:
        workers: Worker dictionaries containing "name" and optional "enabled".
        jobs: Job identifiers to assign, in input order.

    Returns:
        A list of {"job": job, "worker": worker_name} assignment dictionaries.

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
        {
            "job": job,
            "worker": enabled_worker_names[index % worker_count],
        }
        for index, job in enumerate(jobs)
    ]
