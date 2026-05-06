"""
dependency_order.py

Provides plan_batches: topological-sort a dependency graph into parallel batches.
"""

from collections import deque


def plan_batches(dependencies: dict[str, list[str]]) -> list[list[str]]:
    """
    Return batches of tasks that can run in parallel.

    Each batch is a sorted list of tasks whose prerequisites have all been
    satisfied by earlier batches.  Raises ValueError if the graph contains a
    cycle.  Tasks that appear only as dependencies (not as keys) are included.
    The input is not mutated.
    """
    graph = _build_graph(dependencies)
    return _kahn_batches(graph)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _build_graph(dependencies: dict[str, list[str]]) -> dict[str, list[str]]:
    """
    Return a clean adjacency map that includes every node, even those that
    appear only as dependency values.  The returned dict is a fresh copy.
    """
    graph: dict[str, list[str]] = {}

    for task, prereqs in dependencies.items():
        if task not in graph:
            graph[task] = []
        for prereq in prereqs:
            if prereq not in graph:
                graph[prereq] = []
            graph[task].append(prereq)

    return graph


def _in_degrees(graph: dict[str, list[str]]) -> dict[str, int]:
    """
    Count how many tasks must precede each node (number of prerequisites).
    'graph[node]' holds the prerequisites of 'node'.
    """
    counts = {node: 0 for node in graph}
    for prereqs in graph.values():
        for prereq in prereqs:
            counts[prereq]  # already present; just a presence check
    # Each entry in graph[node] is a prerequisite *of* node, so node's
    # in-degree (in a "who depends on me" sense) is the count of tasks that
    # list it as a prereq.  For Kahn's algorithm we need the number of
    # unsatisfied prerequisites *for* each node.
    in_deg = {node: len(prereqs) for node, prereqs in graph.items()}
    return in_deg


def _reverse_edges(graph: dict[str, list[str]]) -> dict[str, list[str]]:
    """
    Build a successor map: for each prereq, which tasks depend on it?
    """
    successors: dict[str, list[str]] = {node: [] for node in graph}
    for node, prereqs in graph.items():
        for prereq in prereqs:
            successors[prereq].append(node)
    return successors


def _kahn_batches(graph: dict[str, list[str]]) -> list[list[str]]:
    """
    Kahn's algorithm, extended to collect nodes layer by layer.

    A node is ready when its in-degree (number of unsatisfied prerequisites)
    reaches zero.
    """
    in_deg = _in_degrees(graph)
    successors = _reverse_edges(graph)

    ready = deque(sorted(node for node, deg in in_deg.items() if deg == 0))
    batches: list[list[str]] = []
    processed = 0

    while ready:
        batch = sorted(ready)
        batches.append(batch)
        ready.clear()

        for node in batch:
            processed += 1
            for dependent in successors[node]:
                in_deg[dependent] -= 1
                if in_deg[dependent] == 0:
                    ready.append(dependent)

        ready = deque(sorted(ready))

    if processed != len(graph):
        raise ValueError("Cycle detected in the dependency graph.")

    return batches
