from collections.abc import Mapping


def _validated_items(dependencies: dict[str, list[str]]) -> list[tuple[str, list[str]]]:
    if not isinstance(dependencies, Mapping):
        raise TypeError("dependencies must be a mapping of task names to dependency lists")

    items: list[tuple[str, list[str]]] = []

    for task, prerequisites in dependencies.items():
        if not isinstance(task, str):
            raise TypeError("task names must be strings")

        if not isinstance(prerequisites, list):
            raise TypeError(f"dependencies for {task!r} must be a list of task names")

        for prerequisite in prerequisites:
            if not isinstance(prerequisite, str):
                raise TypeError(f"dependency names for {task!r} must be strings")

        items.append((task, list(prerequisites)))

    return items


def _build_prerequisite_sets(
    items: list[tuple[str, list[str]]],
) -> dict[str, set[str]]:
    tasks: set[str] = set()

    for task, prerequisites in items:
        tasks.add(task)
        tasks.update(prerequisites)

    prerequisite_sets = {task: set() for task in tasks}

    for task, prerequisites in items:
        prerequisite_sets[task].update(prerequisites)

    return prerequisite_sets


def _build_dependents(prerequisites: dict[str, set[str]]) -> dict[str, set[str]]:
    dependents = {task: set() for task in prerequisites}

    for task, required_tasks in prerequisites.items():
        for required_task in required_tasks:
            dependents[required_task].add(task)

    return dependents


def plan_batches(dependencies: dict[str, list[str]]) -> list[list[str]]:
    items = _validated_items(dependencies)
    remaining_prerequisites = _build_prerequisite_sets(items)
    dependents = _build_dependents(remaining_prerequisites)

    ready = sorted(
        task
        for task, prerequisites in remaining_prerequisites.items()
        if not prerequisites
    )

    batches: list[list[str]] = []
    completed_count = 0

    while ready:
        batch = ready
        batches.append(batch)
        completed_count += len(batch)

        next_ready: list[str] = []

        for completed_task in batch:
            for dependent in dependents[completed_task]:
                remaining_prerequisites[dependent].remove(completed_task)
                if not remaining_prerequisites[dependent]:
                    next_ready.append(dependent)

        ready = sorted(next_ready)

    if completed_count != len(remaining_prerequisites):
        raise ValueError("dependency graph contains a cycle")

    return batches
