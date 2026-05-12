"""
dependency_order.py

Provides plan_batches: topological-sort a dependency graph into parallel batches.
"""

from collections import deque


def plan_batches(dependencies: dict[str, list[str]]) -> list[list[str]]:
    """
    Return batches of tasks that can run in parallel.

    Each batch is a sorted list of tasks whose dependencies are all satisfied
    by previous batches. Raises ValueError if the graph contains a cycle.
    Tasks that appear only as dependencies (not as keys) are included.
    The input is not mutated.
    """
    graph = _build_complete_graph(dependencies)
    in_degree = _compute_in_degrees(graph)
    dependents = _build_dependents(graph)
    return _kahn_batches(graph, in_degree, dependents)


def _build_complete_graph(dependencies: dict[str, list[str]]) -> dict[str, list[str]]:
    """
    Return a copy of dependencies that also includes tasks appearing only
    as dependency values (with empty prerequisite lists).
    """
    graph: dict[str, list[str]] = {}
    for task, prereqs in dependencies.items():
        graph[task] = list(prereqs)
        for prereq in prereqs:
            if prereq not in graph:
                graph[prereq] = []
    return graph


def _compute_in_degrees(graph: dict[str, list[str]]) -> dict[str, int]:
    """
    Return a mapping from each task to the number of tasks that must precede it.

    In this graph, edges point from a task to its prerequisites,
    so in_degree counts how many tasks depend on each task (i.e. outgoing in
    the dependency direction). We want the count of prerequisites per task.
    """
    in_degree = {task: 0 for task in graph}
    for task, prereqs in graph.items():
        in_degree[task] = len(prereqs)
    return in_degree


def _build_dependents(graph: dict[str, list[str]]) -> dict[str, list[str]]:
    """
    Return a map from each task to the list of tasks that directly depend on it.
    """
    dependents: dict[str, list[str]] = {task: [] for task in graph}
    for task, prereqs in graph.items():
        for prereq in prereqs:
            dependents[prereq].append(task)
    return dependents


def _next_ready(in_degree: dict[str, int]) -> list[str]:
    """Return sorted tasks with in_degree zero."""
    return sorted(task for task, deg in in_degree.items() if deg == 0)


def _release_dependents(
    batch: list[str],
    dependents: dict[str, list[str]],
    in_degree: dict[str, int],
) -> None:
    """Decrement in_degree for each dependent of tasks in the batch."""
    for task in batch:
        for dependent in dependents[task]:
            in_degree[dependent] -= 1


def _kahn_batches(
    graph: dict[str, list[str]],
    in_degree: dict[str, int],
    dependents: dict[str, list[str]],
) -> list[list[str]]:
    """
    Execute Kahn's algorithm, collecting tasks into parallel batches.
    Raises ValueError if a cycle prevents all tasks from being scheduled.
    """
    in_degree = dict(in_degree)  # local copy to avoid mutation
    batches: list[list[str]] = []
    scheduled = 0

    ready = _next_ready(in_degree)
    while ready:
        batches.append(ready)
        scheduled += len(ready)
        for task in ready:
            del in_degree[task]
        _release_dependents(ready, dependents, in_degree)
        ready = _next_ready(in_degree)

    if scheduled != len(graph):
        raise ValueError("Cycle detected in the dependency graph.")

    return batches
