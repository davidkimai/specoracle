def assign_round_robin(workers: list[dict], jobs: list[str]) -> list[dict]:
    enabled_workers = [w["name"] for w in workers if w.get("enabled", True)]
    if not enabled_workers:
        raise ValueError("No enabled workers available.")
    result = []
    for i, job in enumerate(jobs):
        worker = enabled_workers[i % len(enabled_workers)]
        result.append({"job": job, "worker": worker})
    return result
