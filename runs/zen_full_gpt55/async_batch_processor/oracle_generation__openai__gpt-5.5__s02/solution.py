import asyncio


def _require_positive_integer(value, name):
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be a positive integer")
    if value <= 0:
        raise ValueError(f"{name} must be positive")


def _split_into_batches(items, batch_size):
    try:
        iterator = iter(items)
    except TypeError as error:
        raise TypeError("items must be iterable") from error

    batches = []
    batch = []

    for item in iterator:
        batch.append(item)
        if len(batch) == batch_size:
            batches.append(batch)
            batch = []

    if batch:
        batches.append(batch)

    return batches


async def _run_handler(handler, batch):
    result = await handler(batch)
    if not isinstance(result, list):
        raise TypeError("handler must return a list")
    return result


async def _worker(queue, handler, results):
    while True:
        try:
            batch_index, batch = queue.get_nowait()
        except asyncio.QueueEmpty:
            return

        results[batch_index] = await _run_handler(handler, batch)


async def _wait_for_tasks(tasks):
    try:
        await asyncio.gather(*tasks)
    except BaseException:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        raise


def _flatten_results(batch_results):
    flattened = []

    for index, result in enumerate(batch_results):
        if result is None:
            raise RuntimeError(f"missing result for batch {index}")
        flattened.extend(result)

    return flattened


async def process_in_batches(
    items,
    handler,
    *,
    batch_size: int,
    concurrency: int,
) -> list:
    _require_positive_integer(batch_size, "batch_size")
    _require_positive_integer(concurrency, "concurrency")

    if not callable(handler):
        raise TypeError("handler must be callable")

    batches = _split_into_batches(items, batch_size)
    if not batches:
        return []

    queue = asyncio.Queue()
    for indexed_batch in enumerate(batches):
        queue.put_nowait(indexed_batch)

    results = [None] * len(batches)
    worker_count = min(concurrency, len(batches))
    tasks = [
        asyncio.create_task(_worker(queue, handler, results))
        for _ in range(worker_count)
    ]

    await _wait_for_tasks(tasks)
    return _flatten_results(results)
