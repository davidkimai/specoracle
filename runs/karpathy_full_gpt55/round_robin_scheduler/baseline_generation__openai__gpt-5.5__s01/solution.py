"""Round-robin job assignment module."""


def assign_round_robin(workers: list[dict], jobs: list[str]) -> list[dict]:
    """
    Assign jobs to enabled workers in round-robin order.

    Each worker dictionary must contain a "name" field and may contain an
    "enabled" field. Workers are considered enabled unless "enabled" is falsey.

    Args:
        workers: Worker dictionaries containing "name" and optional "enabled".
        jobs: Job identifiers to assign.

    Returns:
        A list of dictionaries shaped as {"job": job, "worker": worker_name}.

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
