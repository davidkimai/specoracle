def assign_round_robin(workers: list[dict], jobs: list[str]) -> list[dict]:
    enabled = [w["name"] for w in workers if w.get("enabled", True)]
    if not enabled:
        raise ValueError("No enabled workers")
    return [{"job": job, "worker": enabled[i % len(enabled)]} for i, job in enumerate(jobs)]
