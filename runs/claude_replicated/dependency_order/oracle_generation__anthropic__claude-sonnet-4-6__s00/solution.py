"""
dependency_order.py

Implements plan_batches: topological-sort a dependency graph into parallel batches.
"""

from collections import deque


def plan_batches(dependencies: dict[str, list[str]]) -> list[list[str]]:
    """
    Return batches of tasks that can run in parallel.

    Each batch is a sorted list of tasks whose dependencies have all been
    satisfied by previous batches. Raises ValueError if the graph has a cycle.
    Tasks that appear only as dependencies (not as keys) are included.
    The input is not mutated.
    """
    graph = _build_full_graph(dependencies)
    in_degree = _compute_in_degrees(graph)
    return _kahn_batches(graph, in_degree)


def _build_full_graph(dependencies: dict[str, list[str]]) -> dict[str, list[str]]:
    """
    Return a copy of the dependency graph that includes every node,
    even those that appear only as a dependency value.
    """
    graph: dict[str, list[str]] = {}
    for task, deps in dependencies.items():
        graph[task] = list(deps)
        for dep in deps:
            if dep not in graph:
                graph[dep] = []
    return graph


def _compute_in_degrees(graph: dict[str, list[str]]) -> dict[str, int]:
    """
    Return a mapping of task -> number of tasks that must precede it.
    """
    in_degree = {task: 0 for task in graph}
    for deps in graph.values():
        for dep in deps:
            in_degree[dep] += 1
    return in_degree


def _kahn_batches(
    graph: dict[str, list[str]],
    in_degree: dict[str, int],
) -> list[list[str]]:
    """
    Run Kahn's algorithm, collecting tasks with zero in-degree into batches.

    Each iteration gathers all currently-ready tasks as one parallel batch,
    then decrements in-degrees for their successors.

    Raises ValueError if not all tasks are processed (cycle detected).
    """
    # Build reverse map: dep -> tasks that depend on dep
    dependents: dict[str, list[str]] = {task: [] for task in graph}
    for task, deps in graph.items():
        for dep in deps:
            dependents[dep].append(task)

    ready = deque(task for task, deg in in_degree.items() if deg == 0)
    remaining_degree = dict(in_degree)
    batches: list[list[str]] = []
    processed = 0

    while ready:
        batch = sorted(ready)
        ready.clear()
        batches.append(batch)
        processed += len(batch)

        for task in batch:
            for dependent in dependents[task]:
                remaining_degree[dependent] -= 1
                if remaining_degree[dependent] == 0:
                    ready.append(dependent)

    if processed != len(graph):
        raise ValueError("Cycle detected in dependency graph.")

    return batches
