def assign_round_robin(workers: list[dict], jobs: list[str]) -> list[dict]:
    """Assign jobs to enabled workers in round-robin order without mutating inputs."""
    enabled_workers = [worker for worker in workers if worker.get("enabled", True)]
    if not enabled_workers:
        raise ValueError("no enabled workers")

    return [
        {"job": job, "worker": enabled_workers[index % len(enabled_workers)]["name"]}
        for index, job in enumerate(jobs)
    ]
