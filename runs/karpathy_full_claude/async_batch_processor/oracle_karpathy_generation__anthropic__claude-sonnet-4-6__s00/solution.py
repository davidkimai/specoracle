import asyncio


async def process_in_batches(items, handler, *, batch_size: int, concurrency: int) -> list:
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    if concurrency <= 0:
        raise ValueError("concurrency must be positive")

    items = list(items)
    batches = [items[i:i + batch_size] for i in range(0, len(items), batch_size)]

    results = [None] * len(batches)
    semaphore = asyncio.Semaphore(concurrency)

    async def run_batch(index, batch):
        async with semaphore:
            results[index] = await handler(batch)

    await asyncio.gather(*(run_batch(i, batch) for i, batch in enumerate(batches)))

    return [item for batch_result in results for item in batch_result]
