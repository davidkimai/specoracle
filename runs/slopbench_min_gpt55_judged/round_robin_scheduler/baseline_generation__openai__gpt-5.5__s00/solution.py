def assign_round_robin(workers: list[dict], jobs: list[str]) -> list[dict]:
    """
    Assign jobs to enabled workers in round-robin order.

    Each worker is expected to have a "name" field and may have an "enabled"
    field. If "enabled" is absent, the worker is considered enabled.

    Args:
        workers: A list of worker dictionaries.
        jobs: A list of job identifiers.

    Returns:
        A list of dictionaries shaped as {"job": str, "worker": str}.

    Raises:
        ValueError: If there are no enabled workers.
    """
    enabled_workers = [
        worker["name"]
        for worker in workers
        if worker.get("enabled", True)
    ]

    if not enabled_workers:
        raise ValueError("no enabled workers")

    worker_count = len(enabled_workers)
    return [
        {"job": job, "worker": enabled_workers[index % worker_count]}
        for index, job in enumerate(jobs)
    ]
