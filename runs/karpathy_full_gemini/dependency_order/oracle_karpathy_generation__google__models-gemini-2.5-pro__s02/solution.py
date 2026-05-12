def plan_batches(dependencies: dict[str, list[str]]) -> list[list[str]]:
    """
    Computes an execution plan for a set of tasks with dependencies.

    The plan is a list of batches, where each batch is a list of tasks that
    can be executed in parallel. The batches are ordered sequentially.

    Args:
        dependencies: A dictionary mapping a task name to a list of its
                      prerequisites. Tasks can also be mentioned only as
                      prerequisites.

    Returns:
        A list of batches (lists of task names). Each batch is sorted
        alphabetically.

    Raises:
        ValueError: If the dependency graph contains a cycle.
    """
    # Step 1: Collect all unique tasks from keys and values.
    all_tasks = set(dependencies.keys())
    for prereqs in dependencies.values():
        all_tasks.update(prereqs)

    if not all_tasks:
        return []

    # Step 2: Build graph representations.
    # adj: maps a task to the list of tasks that depend on it (successors).
    # in_degree: maps a task to the number of its prerequisites.
    adj = {task: [] for task in all_tasks}
    in_degree = {task: 0 for task in all_tasks}

    for task, prereqs in dependencies.items():
        for prereq in prereqs:
            # An edge exists from prereq -> task.
            adj[prereq].append(task)
            in_degree[task] += 1

    # Step 3: Initialize a queue with tasks that have no prerequisites.
    # These tasks can be executed in the first batch.
    queue = [task for task in all_tasks if in_degree[task] == 0]

    batches = []
    processed_count = 0

    # Step 4: Process tasks in batches using Kahn's algorithm for topological sort.
    while queue:
        # The current queue contains all tasks for the next batch.
        # Sort alphabetically as required by the spec.
        current_batch = sorted(queue)
        batches.append(current_batch)
        processed_count += len(current_batch)

        # Prepare the queue for the subsequent batch.
        next_queue = []
        for task in current_batch:
            # For each completed task, update its successors.
            for successor in adj[task]:
                in_degree[successor] -= 1
                # If a successor has no remaining prerequisites, it's ready.
                if in_degree[successor] == 0:
                    next_queue.append(successor)

        queue = next_queue

    # Step 5: If not all tasks were processed, the graph contains a cycle.
    if processed_count != len(all_tasks):
        raise ValueError("Dependency graph contains a cycle.")

    return batches
