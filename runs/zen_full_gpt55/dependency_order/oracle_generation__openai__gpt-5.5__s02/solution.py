def _require_task_name(value: object, context: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{context} must be a string")
    return value


def _require_dependency_list(value: object, task: str) -> list[str]:
    if not isinstance(value, list):
        raise TypeError(f"dependencies for {task!r} must be a list of strings")
    return value


def _build_prerequisite_map(
    dependencies: dict[str, list[str]],
) -> dict[str, set[str]]:
    if not isinstance(dependencies, dict):
        raise TypeError("dependencies must be a dict mapping strings to lists of strings")

    prerequisite_map: dict[str, set[str]] = {}

    for raw_task, raw_prerequisites in dependencies.items():
        task = _require_task_name(raw_task, "task name")
        prerequisites = _require_dependency_list(raw_prerequisites, task)

        task_prerequisites = prerequisite_map.setdefault(task, set())

        for raw_prerequisite in prerequisites:
            prerequisite = _require_task_name(
                raw_prerequisite,
                f"dependency of {task!r}",
            )
            task_prerequisites.add(prerequisite)
            prerequisite_map.setdefault(prerequisite, set())

    return prerequisite_map


def _cycle_error(remaining: dict[str, set[str]]) -> ValueError:
    tasks = ", ".join(sorted(remaining))
    return ValueError(f"dependency graph contains a cycle involving: {tasks}")


def plan_batches(dependencies: dict[str, list[str]]) -> list[list[str]]:
    prerequisite_map = _build_prerequisite_map(dependencies)
    remaining = {task: set(prerequisites) for task, prerequisites in prerequisite_map.items()}
    batches: list[list[str]] = []

    while remaining:
        ready = sorted(task for task, prerequisites in remaining.items() if not prerequisites)

        if not ready:
            raise _cycle_error(remaining)

        batches.append(ready)
        completed_now = set(ready)

        remaining = {
            task: prerequisites - completed_now
            for task, prerequisites in remaining.items()
            if task not in completed_now
        }

    return batches
