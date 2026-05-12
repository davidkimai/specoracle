from __future__ import annotations


def _require_worker_name(worker: dict, index: int) -> str:
    if "name" not in worker:
        raise ValueError(f"worker at index {index} is missing required field 'name'")

    name = worker["name"]
    if not isinstance(name, str):
        raise TypeError(f"worker at index {index} has non-string 'name'")

    return name


def _require_worker_enabled(worker: dict, index: int) -> bool:
    enabled = worker.get("enabled", True)
    if not isinstance(enabled, bool):
        raise TypeError(f"worker at index {index} has non-boolean 'enabled'")

    return enabled


def _enabled_worker_names(workers: list[dict]) -> list[str]:
    if not isinstance(workers, list):
        raise TypeError("workers must be a list of dictionaries")

    names: list[str] = []

    for index, worker in enumerate(workers):
        if not isinstance(worker, dict):
            raise TypeError(f"worker at index {index} is not a dictionary")

        name = _require_worker_name(worker, index)
        enabled = _require_worker_enabled(worker, index)

        if enabled:
            names.append(name)

    return names


def _validated_jobs(jobs: list[str]) -> list[str]:
    if not isinstance(jobs, list):
        raise TypeError("jobs must be a list of strings")

    for index, job in enumerate(jobs):
        if not isinstance(job, str):
            raise TypeError(f"job at index {index} is not a string")

    return list(jobs)


def assign_round_robin(workers: list[dict], jobs: list[str]) -> list[dict]:
    enabled_names = _enabled_worker_names(workers)
    if not enabled_names:
        raise ValueError("no enabled workers")

    job_values = _validated_jobs(jobs)
    worker_count = len(enabled_names)

    return [
        {"job": job, "worker": enabled_names[index % worker_count]}
        for index, job in enumerate(job_values)
    ]
