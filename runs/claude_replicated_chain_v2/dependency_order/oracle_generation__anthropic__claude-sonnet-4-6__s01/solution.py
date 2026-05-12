"""
dependency_order.py

Topological batch scheduler using Kahn's algorithm.
"""

from collections import deque


def plan_batches(dependencies: dict[str, list[str]]) -> list[list[str]]:
    """
    Return batches of tasks that can run in parallel.

    Each batch is a sorted list of tasks whose prerequisites are satisfied
    by all previous batches.  Raises ValueError if the graph contains a cycle.
    """
    graph = _build_graph(dependencies)
    return _kahn_batches(graph)


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


def _in_degrees(graph: dict[str, list[str]]) -> dict[str, int]:
    """Count how many prerequisites each node has."""
    degrees = {node: 0 for node in graph}
    for prereqs in graph.values():
        for prereq in prereqs:
            degrees[prereq] = degrees.get(prereq, 0)  # already initialised above
    # Actually count incoming edges (node -> its dependents means node is a prereq of others)
    # graph[task] = prereqs of task, so each prereq has an outgoing edge to task.
    # In-degree of a task = number of tasks that list it as a prereq.
    degrees = {node: 0 for node in graph}
    for task, prereqs in graph.items():
        for prereq in prereqs:
            # prereq must finish before task, so task has task as a dependent of prereq.
            # in-degree counts how many prereqs a node has.
            pass
    # Simpler direct approach: in-degree[task] = len(graph[task])
    return {node: len(prereqs) for node, prereqs in graph.items()}


def _reverse_edges(graph: dict[str, list[str]]) -> dict[str, list[str]]:
    """
    Build a reverse adjacency map: for each node, which nodes depend on it.
    (prereq -> list of tasks that need prereq)
    """
    reverse: dict[str, list[str]] = {node: [] for node in graph}
    for task, prereqs in graph.items():
        for prereq in prereqs:
            reverse[prereq].append(task)
    return reverse


def _kahn_batches(graph: dict[str, list[str]]) -> list[list[str]]:
    """
    Kahn's algorithm adapted to produce level-by-level batches.
    graph[task] = list of prerequisite tasks.
    """
    in_degree = _in_degrees(graph)
    dependents = _reverse_edges(graph)  # prereq -> tasks that depend on it

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

    if visited != len(graph):
        raise ValueError("Cycle detected in the dependency graph.")

    return batches
