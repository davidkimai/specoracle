from __future__ import annotations


def plan_batches(dependencies: dict[str, list[str]]) -> list[list[str]]:
    """Return parallel execution batches for tasks with prerequisite dependencies."""
    prerequisites = _normalized_prerequisites(dependencies)

    batches: list[list[str]] = []
    completed: set[str] = set()
    remaining = {task: set(required) for task, required in prerequisites.items()}

    while remaining:
        ready = sorted(
            task for task, required in remaining.items() if required <= completed
        )

        if not ready:
            raise ValueError("dependency graph contains a cycle")

        batches.append(ready)
        completed.update(ready)

        for task in ready:
            del remaining[task]

    return batches


def _normalized_prerequisites(
    dependencies: dict[str, list[str]],
) -> dict[str, set[str]]:
    if not isinstance(dependencies, dict):
        raise TypeError("dependencies must be a dict[str, list[str]]")

    prerequisites: dict[str, set[str]] = {}
    all_tasks: set[str] = set()

    for task, required_tasks in dependencies.items():
        _require_string(task, "task name")

        if not isinstance(required_tasks, list):
            raise TypeError(f"dependencies for {task!r} must be a list[str]")

        required_set = set()
        for required_task in required_tasks:
            _require_string(required_task, f"dependency of {task!r}")
            required_set.add(required_task)

        prerequisites[task] = required_set
        all_tasks.add(task)
        all_tasks.update(required_set)

    for task in all_tasks:
        prerequisites.setdefault(task, set())

    return prerequisites


def _require_string(value: object, description: str) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{description} must be a str")
