from __future__ import annotations


def assign_round_robin(workers: list[dict], jobs: list[str]) -> list[dict]:
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
