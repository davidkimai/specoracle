"""
dependency_order.py

Provides plan_batches: topological-sort a dependency graph into parallel batches.
"""

from collections import deque


def plan_batches(
    dependencies: dict[str, list[str]],
    *,
    completed: set[str] | None = None,
) -> list[list[str]]:
    """
    Return batches of tasks that can run in parallel.

    Each batch is a sorted list of tasks whose prerequisites have all been
    satisfied by earlier batches.  Raises ValueError if the graph contains a
    cycle.  Tasks that appear only as dependencies (not as keys) are included.
    The input is not mutated.

    If *completed* is provided, those tasks are treated as already finished:
    they satisfy dependencies for remaining tasks but do not appear in any
    returned batch.
    """
    done: set[str] = set(completed) if completed else set()
    graph = _build_graph(dependencies)
    return _kahn_batches(graph, done)


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


def _in_degrees(graph: dict[str, list[str]], done: set[str]) -> dict[str, int]:
    """
    Count unsatisfied prerequisites for each node, treating *done* tasks as
    already satisfied.
    """
    in_deg: dict[str, int] = {}
    for node, prereqs in graph.items():
        if node in done:
            continue
        in_deg[node] = sum(1 for p in prereqs if p not in done)
    return in_deg


def _reverse_edges(graph: dict[str, list[str]], done: set[str]) -> dict[str, list[str]]:
    """
    Build a successor map: for each prereq, which tasks depend on it?
    Only considers nodes that are not in *done*.
    """
    successors: dict[str, list[str]] = {node: [] for node in graph if node not in done}
    for node, prereqs in graph.items():
        if node in done:
            continue
        for prereq in prereqs:
            if prereq in done:
                continue
            successors[prereq].append(node)
    return successors


def _kahn_batches(graph: dict[str, list[str]], done: set[str]) -> list[list[str]]:
    """
    Kahn's algorithm, extended to collect nodes layer by layer.

    A node is ready when its in-degree (number of unsatisfied prerequisites)
    reaches zero.  Nodes in *done* are excluded from output but their
    dependencies are pre-satisfied.
    """
    in_deg = _in_degrees(graph, done)
    successors = _reverse_edges(graph, done)

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

    if processed != len(in_deg):
        raise ValueError("Cycle detected in the dependency graph.")

    return batches
