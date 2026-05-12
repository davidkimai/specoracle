from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping


def plan_batches(dependencies: dict[str, list[str]]) -> list[list[str]]:
    """Return alphabetized parallel execution batches for a dependency graph.

    The input maps each task to the tasks that must complete before it can run.
    Tasks that appear only as dependencies are included. A cycle raises
    ValueError.
    """
    _validate_dependencies(dependencies)

    tasks = _collect_tasks(dependencies)
    prerequisite_count, dependents = _build_graph(dependencies, tasks)

    batches: list[list[str]] = []
    ready = sorted(task for task in tasks if prerequisite_count[task] == 0)
    completed_count = 0

    while ready:
        batch = ready
        batches.append(batch)
        completed_count += len(batch)

        next_ready: list[str] = []
        for completed_task in batch:
            for dependent in dependents[completed_task]:
                prerequisite_count[dependent] -= 1
                if prerequisite_count[dependent] == 0:
                    next_ready.append(dependent)

        ready = sorted(next_ready)

    if completed_count != len(tasks):
        raise ValueError("dependency graph contains a cycle")

    return batches


def _validate_dependencies(dependencies: object) -> None:
    if not isinstance(dependencies, Mapping):
        raise TypeError("dependencies must be a mapping of task names to lists of prerequisite task names")

    for task, prerequisites in dependencies.items():
        if not isinstance(task, str):
            raise TypeError("task names must be strings")
        if not isinstance(prerequisites, list):
            raise TypeError("each dependency value must be a list of prerequisite task names")
        for prerequisite in prerequisites:
            if not isinstance(prerequisite, str):
                raise TypeError("prerequisite task names must be strings")


def _collect_tasks(dependencies: Mapping[str, list[str]]) -> set[str]:
    tasks = set(dependencies)

    for prerequisites in dependencies.values():
        tasks.update(prerequisites)

    return tasks


def _build_graph(
    dependencies: Mapping[str, list[str]],
    tasks: set[str],
) -> tuple[dict[str, int], dict[str, set[str]]]:
    prerequisite_count = {task: 0 for task in tasks}
    dependents: dict[str, set[str]] = defaultdict(set)

    for task, prerequisites in dependencies.items():
        unique_prerequisites = set(prerequisites)
        prerequisite_count[task] = len(unique_prerequisites)

        for prerequisite in unique_prerequisites:
            dependents[prerequisite].add(task)

    return prerequisite_count, dependents
