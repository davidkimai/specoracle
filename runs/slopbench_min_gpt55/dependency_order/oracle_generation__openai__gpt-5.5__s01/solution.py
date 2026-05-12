from collections.abc import Mapping, Sequence


def plan_batches(dependencies: dict[str, list[str]]) -> list[list[str]]:
    """Return parallel execution batches for tasks with prerequisites."""
    _validate_dependencies(dependencies)

    tasks = _collect_tasks(dependencies)
    dependents, remaining_prerequisites = _build_graph(dependencies, tasks)

    batches: list[list[str]] = []
    ready = sorted(
        task for task, count in remaining_prerequisites.items() if count == 0
    )
    completed_count = 0

    while ready:
        batch = ready
        batches.append(batch)
        completed_count += len(batch)

        next_ready: list[str] = []
        for task in batch:
            for dependent in dependents[task]:
                remaining_prerequisites[dependent] -= 1
                if remaining_prerequisites[dependent] == 0:
                    next_ready.append(dependent)

        ready = sorted(next_ready)

    if completed_count != len(tasks):
        raise ValueError("dependency graph contains a cycle")

    return batches


def _validate_dependencies(dependencies: object) -> None:
    if not isinstance(dependencies, Mapping):
        raise TypeError("dependencies must be a mapping of task names to lists")

    for task, prerequisites in dependencies.items():
        if not isinstance(task, str):
            raise TypeError("task names must be strings")

        if not isinstance(prerequisites, Sequence) or isinstance(
            prerequisites, (str, bytes)
        ):
            raise TypeError("each task's dependencies must be a list of strings")

        for prerequisite in prerequisites:
            if not isinstance(prerequisite, str):
                raise TypeError("dependency task names must be strings")


def _collect_tasks(dependencies: Mapping[str, Sequence[str]]) -> set[str]:
    tasks = set(dependencies)

    for prerequisites in dependencies.values():
        tasks.update(prerequisites)

    return tasks


def _build_graph(
    dependencies: Mapping[str, Sequence[str]],
    tasks: set[str],
) -> tuple[dict[str, set[str]], dict[str, int]]:
    dependents: dict[str, set[str]] = {task: set() for task in tasks}
    remaining_prerequisites: dict[str, int] = {}

    for task in tasks:
        prerequisites = set(dependencies.get(task, ()))
        remaining_prerequisites[task] = len(prerequisites)

        for prerequisite in prerequisites:
            dependents[prerequisite].add(task)

    return dependents, remaining_prerequisites
