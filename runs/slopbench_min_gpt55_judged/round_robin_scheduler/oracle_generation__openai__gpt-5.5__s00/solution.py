__all__ = ["assign_round_robin"]


def assign_round_robin(workers: list[dict], jobs: list[str]) -> list[dict]:
    """Assign jobs to enabled workers in round-robin order."""
    worker_names = _enabled_worker_names(workers)
    if not worker_names:
        raise ValueError("no enabled workers")

    _validate_jobs(jobs)

    worker_count = len(worker_names)
    return [
        {"job": job, "worker": worker_names[index % worker_count]}
        for index, job in enumerate(jobs)
    ]


def _enabled_worker_names(workers: list[dict]) -> list[str]:
    if not isinstance(workers, list):
        raise TypeError("workers must be a list of dictionaries")

    names: list[str] = []

    for index, worker in enumerate(workers):
        _validate_worker(worker, index)
        if worker.get("enabled", True):
            names.append(worker["name"])

    return names


def _validate_worker(worker: dict, index: int) -> None:
    if not isinstance(worker, dict):
        raise TypeError(f"workers[{index}] must be a dictionary")

    if "name" not in worker:
        raise ValueError(f"workers[{index}] is missing required field 'name'")

    if not isinstance(worker["name"], str):
        raise TypeError(f"workers[{index}]['name'] must be a string")

    enabled = worker.get("enabled", True)
    if not isinstance(enabled, bool):
        raise TypeError(f"workers[{index}]['enabled'] must be a boolean")


def _validate_jobs(jobs: list[str]) -> None:
    if not isinstance(jobs, list):
        raise TypeError("jobs must be a list of strings")

    for index, job in enumerate(jobs):
        if not isinstance(job, str):
            raise TypeError(f"jobs[{index}] must be a string")
