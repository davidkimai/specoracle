"""A module for planning task execution batches based on dependencies."""

from __future__ import annotations


def plan_batches(dependencies: dict[str, list[str]]) -> list[list[str]]:
    """Calculates an execution plan of parallelizable task batches.

    This function performs a topological sort of the tasks defined in the
    dependency graph. Each list in the output represents a batch of tasks that
    can be executed in parallel. The batches are ordered sequentially; all tasks
    in batch `i` must be completed before any task in batch `i+1` can begin.

    The tasks within each batch are sorted alphabetically.

    Args:
        dependencies: A dictionary mapping a task name to a list of its
            prerequisite tasks. Tasks that are only dependencies and not
            keys will be included in the plan. The input dictionary is not
            mutated.

    Returns:
        A list of lists, where each inner list is a batch of tasks that can
        be run in parallel, sorted alphabetically.

    Raises:
        ValueError: If the dependency graph contains a cycle, making it
            impossible to create a valid execution plan.
    """
    # Step 1: Gather all unique task names from keys and values.
    # This ensures tasks that are only dependencies are included.
    all_tasks = set(dependencies.keys())
    for prereqs in dependencies.values():
        all_tasks.update(prereqs)

    if not all_tasks:
        return []

    # Step 2: Build the graph representation.
    # - `adj`: An adjacency list for the forward graph (prereq -> task).
    # - `in_degree`: The number of prerequisites for each task.
    adj: dict[str, list[str]] = {task: [] for task in all_tasks}
    in_degree: dict[str, int] = {task: 0 for task in all_tasks}

    for task, prereqs in dependencies.items():
        for prereq in prereqs:
            # An edge exists from prereq -> task
            adj[prereq].append(task)
            in_degree[task] += 1

    # Step 3: Initialize the first batch with tasks that have no prerequisites.
    # This is the starting point for Kahn's algorithm for topological sorting.
    queue = [task for task in all_tasks if in_degree[task] == 0]

    batches = []
    processed_count = 0

    # Step 4: Process tasks in batches.
    while queue:
        # Sort the current batch of parallelizable tasks alphabetically.
        current_batch = sorted(queue)
        batches.append(current_batch)
        processed_count += len(current_batch)

        next_queue = []
        # For each task "completed", decrement the in-degree of its dependents.
        for task in current_batch:
            for dependent_task in adj[task]:
                in_degree[dependent_task] -= 1
                # If a dependent task now has no remaining prerequisites,
                # it can be added to the next batch.
                if in_degree[dependent_task] == 0:
                    next_queue.append(dependent_task)

        queue = next_queue

    # Step 5: Validate the sort. If not all tasks were processed, there's a cycle.
    if processed_count != len(all_tasks):
        raise ValueError("Dependency graph contains a cycle.")

    return batches
