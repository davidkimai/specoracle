import asyncio


async def process_in_batches(items, handler, *, batch_size: int, concurrency: int) -> list:
    """Process a synchronous iterable in list batches with bounded async concurrency."""
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    if concurrency <= 0:
        raise ValueError("concurrency must be positive")

    batches = []
    batch = []
    for item in items:
        batch.append(item)
        if len(batch) == batch_size:
            batches.append(batch)
            batch = []
    if batch:
        batches.append(batch)

    if not batches:
        return []

    semaphore = asyncio.Semaphore(concurrency)

    async def run_batch(batch):
        async with semaphore:
            return await handler(batch)

    tasks = [asyncio.create_task(run_batch(batch)) for batch in batches]
    try:
        batch_results = await asyncio.gather(*tasks)
    except BaseException:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        raise

    results = []
    for batch_result in batch_results:
        results.extend(batch_result)
    return results
