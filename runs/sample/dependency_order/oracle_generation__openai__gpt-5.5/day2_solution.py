def _validate_task_name(name: object, context: str) -> str:
    if not isinstance(name, str):
        raise TypeError(f"{context} must be a string")
    return name


def _validate_completed(completed: set[str] | None) -> set[str]:
    if completed is None:
        return set()

    if not isinstance(completed, set):
        raise TypeError("completed must be a set or None")

    return {
        _validate_task_name(task, "completed task")
        for task in completed
    }


def _build_prerequisite_sets(dependencies: dict[str, list[str]]) -> dict[str, set[str]]:
    if not isinstance(dependencies, dict):
        raise TypeError("dependencies must be a dictionary")

    prerequisite_sets: dict[str, set[str]] = {}

    for task, prerequisites in dependencies.items():
        task_name = _validate_task_name(task, "task name")

        if not isinstance(prerequisites, list):
            raise TypeError(f"dependencies for {task_name!r} must be a list")

        task_prerequisites: set[str] = set()
        for prerequisite in prerequisites:
            prerequisite_name = _validate_task_name(
                prerequisite,
                f"dependency of {task_name!r}",
            )
            task_prerequisites.add(prerequisite_name)
            prerequisite_sets.setdefault(prerequisite_name, set())

        prerequisite_sets[task_name] = task_prerequisites

    return prerequisite_sets


def plan_batches(
    dependencies: dict[str, list[str]],
    *,
    completed: set[str] | None = None,
) -> list[list[str]]:
    remaining = _build_prerequisite_sets(dependencies)
    completed_tasks = _validate_completed(completed)

    if completed_tasks:
        for task in completed_tasks:
            remaining.pop(task, None)

        for prerequisites in remaining.values():
            prerequisites.difference_update(completed_tasks)

    batches: list[list[str]] = []

    while remaining:
        ready_tasks = sorted(
            task for task, prerequisites in remaining.items() if not prerequisites
        )

        if not ready_tasks:
            raise ValueError("dependency graph contains a cycle")

        batches.append(ready_tasks)
        newly_completed = set(ready_tasks)

        for task in ready_tasks:
            del remaining[task]

        for prerequisites in remaining.values():
            prerequisites.difference_update(newly_completed)

    return batches
