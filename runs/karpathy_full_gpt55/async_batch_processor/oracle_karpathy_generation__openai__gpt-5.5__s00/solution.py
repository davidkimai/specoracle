import asyncio


async def process_in_batches(items, handler, *, batch_size: int, concurrency: int) -> list:
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

    semaphore = asyncio.Semaphore(concurrency)

    async def run(batch):
        async with semaphore:
            return await handler(batch)

    batch_results = await asyncio.gather(*(run(batch) for batch in batches))

    results = []
    for result in batch_results:
        results.extend(result)
    return results
