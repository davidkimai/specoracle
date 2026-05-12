"""Round-robin job assignment."""

from typing import Any


def _require_list(value: Any, name: str) -> list[Any]:
    if not isinstance(value, list):
        raise TypeError(f"{name} must be a list")
    return value


def _require_worker(worker: Any, index: int) -> dict[str, Any]:
    if not isinstance(worker, dict):
        raise TypeError(f"workers[{index}] must be a dict")
    return worker


def _worker_name(worker: dict[str, Any], index: int) -> str:
    if "name" not in worker:
        raise ValueError(f"workers[{index}] must include a 'name' field")

    name = worker["name"]
    if not isinstance(name, str):
        raise TypeError(f"workers[{index}]['name'] must be a str")
    return name


def _worker_enabled(worker: dict[str, Any], index: int) -> bool:
    enabled = worker.get("enabled", True)
    if not isinstance(enabled, bool):
        raise TypeError(f"workers[{index}]['enabled'] must be a bool when provided")
    return enabled


def _enabled_worker_names(workers: list[Any]) -> list[str]:
    names: list[str] = []

    for index, worker_value in enumerate(workers):
        worker = _require_worker(worker_value, index)
        name = _worker_name(worker, index)
        if _worker_enabled(worker, index):
            names.append(name)

    return names


def _validate_jobs(jobs: list[Any]) -> None:
    for index, job in enumerate(jobs):
        if not isinstance(job, str):
            raise TypeError(f"jobs[{index}] must be a str")


def assign_round_robin(workers: list[dict], jobs: list[str]) -> list[dict]:
    """Assign jobs to enabled workers in input order using round-robin order."""
    worker_values = _require_list(workers, "workers")
    job_values = _require_list(jobs, "jobs")

    enabled_names = _enabled_worker_names(worker_values)
    if not enabled_names:
        raise ValueError("at least one worker must be enabled")

    _validate_jobs(job_values)

    worker_count = len(enabled_names)
    return [
        {"job": job, "worker": enabled_names[index % worker_count]}
        for index, job in enumerate(job_values)
    ]
