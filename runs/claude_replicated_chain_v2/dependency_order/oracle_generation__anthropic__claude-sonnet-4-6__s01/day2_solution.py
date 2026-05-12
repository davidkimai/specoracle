"""
dependency_order.py

Topological batch scheduler using Kahn's algorithm.
"""

from collections import deque


def plan_batches(
    dependencies: dict[str, list[str]],
    *,
    completed: set[str] | None = None,
) -> list[list[str]]:
    """
    Return batches of tasks that can run in parallel.

    Each batch is a sorted list of tasks whose prerequisites are satisfied
    by all previous batches.  Raises ValueError if the graph contains a cycle.

    If *completed* is provided, those tasks are treated as already finished:
    they are excluded from the returned batches but their completion is
    credited when computing whether remaining tasks are ready to run.
    """
    done: set[str] = set(completed) if completed else set()
    graph = _build_graph(dependencies)
    return _kahn_batches(graph, done)


def _build_graph(dependencies: dict[str, list[str]]) -> dict[str, list[str]]:
    """
    Build a complete adjacency representation that includes every node,
    even those that appear only as dependency values.
    Does not mutate the input.
    """
    graph: dict[str, list[str]] = {}

    for task, prereqs in dependencies.items():
        graph.setdefault(task, list(prereqs))
        for prereq in prereqs:
            graph.setdefault(prereq, [])

    return graph


def _in_degrees(graph: dict[str, list[str]], skip: set[str]) -> dict[str, int]:
    """
    Count how many prerequisites each node has, ignoring nodes in *skip*.
    Nodes in *skip* are excluded from the result entirely.
    """
    degrees = {node: 0 for node in graph if node not in skip}
    for task, prereqs in graph.items():
        if task in skip:
            continue
        for prereq in prereqs:
            if prereq not in skip:
                degrees[task] = degrees.get(task, 0)  # ensure key exists
        # in-degree = number of prereqs that are NOT already skipped
        degrees[task] = sum(1 for p in prereqs if p not in skip)
    return degrees


def _reverse_edges(graph: dict[str, list[str]], skip: set[str]) -> dict[str, list[str]]:
    """
    Build a reverse adjacency map: for each node, which nodes depend on it.
    (prereq -> list of tasks that need prereq), excluding skipped nodes.
    """
    reverse: dict[str, list[str]] = {node: [] for node in graph if node not in skip}
    for task, prereqs in graph.items():
        if task in skip:
            continue
        for prereq in prereqs:
            if prereq not in skip:
                reverse[prereq].append(task)
    return reverse


def _kahn_batches(graph: dict[str, list[str]], skip: set[str]) -> list[list[str]]:
    """
    Kahn's algorithm adapted to produce level-by-level batches.
    graph[task] = list of prerequisite tasks.
    Nodes in *skip* are treated as already completed.
    """
    in_degree = _in_degrees(graph, skip)
    dependents = _reverse_edges(graph, skip)

    ready = deque(sorted(node for node, deg in in_degree.items() if deg == 0))
    batches: list[list[str]] = []
    visited = 0

    while ready:
        batch = sorted(ready)
        batches.append(batch)
        visited += len(batch)
        ready.clear()

        for node in batch:
            for dependent in dependents[node]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    ready.append(dependent)

        ready = deque(sorted(ready))

    if visited != len(in_degree):
        raise ValueError("Cycle detected in the dependency graph.")

    return batches
