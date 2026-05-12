from __future__ import annotations


def plan_batches(dependencies: dict[str, list[str]]) -> list[list[str]]:
    normalized_dependencies = _normalize_dependencies(dependencies)
    tasks = _collect_tasks(normalized_dependencies)
    dependents_by_task, prerequisite_counts = _build_graph(normalized_dependencies, tasks)
    return _make_batches(dependents_by_task, prerequisite_counts)


def _normalize_dependencies(dependencies: dict[str, list[str]]) -> dict[str, set[str]]:
    if not isinstance(dependencies, dict):
        raise TypeError("dependencies must be a dict[str, list[str]]")

    normalized: dict[str, set[str]] = {}

    for task, prerequisites in dependencies.items():
        if not isinstance(task, str):
            raise TypeError("all task names must be strings")

        if not isinstance(prerequisites, list):
            raise TypeError("each dependency value must be a list[str]")

        normalized_prerequisites: set[str] = set()
        for prerequisite in prerequisites:
            if not isinstance(prerequisite, str):
                raise TypeError("all prerequisite task names must be strings")
            normalized_prerequisites.add(prerequisite)

        normalized[task] = normalized_prerequisites

    return normalized


def _collect_tasks(dependencies: dict[str, set[str]]) -> set[str]:
    tasks: set[str] = set(dependencies)

    for prerequisites in dependencies.values():
        tasks.update(prerequisites)

    return tasks


def _build_graph(
    dependencies: dict[str, set[str]],
    tasks: set[str],
) -> tuple[dict[str, list[str]], dict[str, int]]:
    dependents_by_task: dict[str, list[str]] = {task: [] for task in tasks}
    prerequisite_counts: dict[str, int] = {task: 0 for task in tasks}

    for task, prerequisites in dependencies.items():
        prerequisite_counts[task] = len(prerequisites)

        for prerequisite in prerequisites:
            dependents_by_task[prerequisite].append(task)

    for dependents in dependents_by_task.values():
        dependents.sort()

    return dependents_by_task, prerequisite_counts


def _make_batches(
    dependents_by_task: dict[str, list[str]],
    prerequisite_counts: dict[str, int],
) -> list[list[str]]:
    ready = sorted(
        task for task, prerequisite_count in prerequisite_counts.items()
        if prerequisite_count == 0
    )
    batches: list[list[str]] = []
    completed_count = 0

    while ready:
        batch = ready
        batches.append(batch)
        completed_count += len(batch)

        next_ready: list[str] = []
        for task in batch:
            for dependent in dependents_by_task[task]:
                prerequisite_counts[dependent] -= 1
                if prerequisite_counts[dependent] == 0:
                    next_ready.append(dependent)

        ready = sorted(next_ready)

    if completed_count != len(prerequisite_counts):
        raise ValueError("dependency graph contains a cycle")

    return batches
