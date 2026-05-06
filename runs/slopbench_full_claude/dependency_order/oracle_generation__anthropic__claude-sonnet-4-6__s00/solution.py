"""
dependency_order.py

Topological batch scheduler using Kahn's algorithm.
"""

from collections import deque


def plan_batches(dependencies: dict[str, list[str]]) -> list[list[str]]:
    """
    Return batches of tasks that can run in parallel.

    Each batch is a sorted list of tasks whose prerequisites have all
    been satisfied by previous batches.  Raises ValueError if the
    dependency graph contains a cycle.
    """
    graph = _build_graph(dependencies)
    return _kahn_batches(graph)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_graph(dependencies: dict[str, list[str]]) -> dict[str, list[str]]:
    """
    Return a canonical adjacency map that includes every node that
    appears either as a key or as a dependency value.
    """
    graph: dict[str, list[str]] = {}

    for task, prereqs in dependencies.items():
        if task not in graph:
            graph[task] = []
        for prereq in prereqs:
            graph[task].append(prereq)
            if prereq not in graph:
                graph[prereq] = []

    return graph


def _in_degrees(graph: dict[str, list[str]]) -> dict[str, int]:
    """
    Compute in-degree (number of prerequisites) for every node.

    'In-degree' here means the count of tasks that *this* task depends
    on, i.e. the length of its prereq list in the graph.
    """
    return {task: len(prereqs) for task, prereqs in graph.items()}


def _reverse_edges(graph: dict[str, list[str]]) -> dict[str, list[str]]:
    """
    Build a reverse adjacency map: for each prereq, list the tasks
    that directly depend on it.
    """
    reverse: dict[str, list[str]] = {task: [] for task in graph}
    for task, prereqs in graph.items():
        for prereq in prereqs:
            reverse[prereq].append(task)
    return reverse


def _kahn_batches(graph: dict[str, list[str]]) -> list[list[str]]:
    """
    Run Kahn's algorithm, collecting nodes into parallel batches.
    """
    in_deg = _in_degrees(graph)
    dependents = _reverse_edges(graph)

    ready = deque(task for task, deg in in_deg.items() if deg == 0)
    batches: list[list[str]] = []
    processed = 0

    while ready:
        batch = sorted(ready)
        batches.append(batch)
        ready.clear()

        for task in batch:
            processed += 1
            for dependent in dependents[task]:
                in_deg[dependent] -= 1
                if in_deg[dependent] == 0:
                    ready.append(dependent)

    if processed != len(graph):
        raise ValueError("Dependency graph contains a cycle.")

    return batches
