from typing import Any

__all__ = ["assign_round_robin"]


def _require_list(value: Any, parameter_name: str) -> None:
    if not isinstance(value, list):
        raise TypeError(f"{parameter_name} must be a list")


def _worker_name(worker: dict, index: int) -> str:
    if "name" not in worker:
        raise ValueError(f"workers[{index}] is missing required field 'name'")

    name = worker["name"]
    if not isinstance(name, str):
        raise TypeError(f"workers[{index}]['name'] must be a string")

    return name


def _worker_enabled(worker: dict, index: int) -> bool:
    enabled = worker.get("enabled", True)
    if not isinstance(enabled, bool):
        raise TypeError(f"workers[{index}]['enabled'] must be a boolean when present")

    return enabled


def _enabled_worker_names(workers: list[dict]) -> list[str]:
    _require_list(workers, "workers")

    names: list[str] = []
    for index, worker in enumerate(workers):
        if not isinstance(worker, dict):
            raise TypeError(f"workers[{index}] must be a dict")

        name = _worker_name(worker, index)
        if _worker_enabled(worker, index):
            names.append(name)

    return names


def _validate_jobs(jobs: list[str]) -> None:
    _require_list(jobs, "jobs")

    for index, job in enumerate(jobs):
        if not isinstance(job, str):
            raise TypeError(f"jobs[{index}] must be a string")


def assign_round_robin(workers: list[dict], jobs: list[str]) -> list[dict]:
    enabled_names = _enabled_worker_names(workers)
    if not enabled_names:
        raise ValueError("there are no enabled workers")

    _validate_jobs(jobs)

    worker_count = len(enabled_names)
    return [
        {"job": job, "worker": enabled_names[index % worker_count]}
        for index, job in enumerate(jobs)
    ]
