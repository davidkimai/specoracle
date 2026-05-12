def assign_round_robin(workers: list[dict], jobs: list[str]) -> list[dict]:
    """Assign jobs to enabled workers in round-robin order."""
    enabled_workers = [worker for worker in workers if worker.get("enabled", True)]

    if not enabled_workers:
        raise ValueError("no enabled workers")

    assignments = []
    worker_count = len(enabled_workers)

    for index, job in enumerate(jobs):
        worker = enabled_workers[index % worker_count]
        assignments.append({"job": job, "worker": worker["name"]})

    return assignments
