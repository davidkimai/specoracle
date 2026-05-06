"""Round-robin job scheduler."""


def _enabled_workers(workers: list[dict]) -> list[str]:
    return [w["name"] for w in workers if w.get("enabled", True)]


def assign_round_robin(workers: list[dict], jobs: list[str]) -> list[dict]:
    active = _enabled_workers(workers)
    if not active:
        raise ValueError("No enabled workers available.")
    return [
        {"job": job, "worker": active[index % len(active)]}
        for index, job in enumerate(jobs)
    ]
