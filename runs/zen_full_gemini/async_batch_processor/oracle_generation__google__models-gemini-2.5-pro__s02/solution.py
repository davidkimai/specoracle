import asyncio
import itertools
from typing import Awaitable, Callable, Iterable, Iterator, List, TypeVar

# Type variables for generic function signatures.
# T represents the type of an item in the input iterable.
# R represents the type of an item in the result list.
T = TypeVar("T")
R = TypeVar("R")


def _validate_positive_integer(value: int, name: str) -> None:
    """Raise ValueError if the value is not a positive integer."""
    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer, but got {value!r}")


def _create_batches(items: Iterable[T], size: int) -> Iterator[List[T]]:
    """
    Yields successive n-sized chunks from an iterable.

    The last yielded chunk may be smaller than the requested size.
    """
    iterator = iter(items)
    while True:
        # The list constructor consumes the slice from the iterator.
        batch = list(itertools.islice(iterator, size))
        if not batch:
            # When the iterator is exhausted, islice returns an empty sequence.
            break
        yield batch


async def _process_batch_with_semaphore(
    handler: Callable[[List[T]], Awaitable[List[R]]],
    batch: List[T],
    semaphore: asyncio.Semaphore,
) -> List[R]:
    """
    Acquire a semaphore, run the handler on a batch, and release the semaphore.

    This helper encapsulates the concurrency control logic for a single batch.
    """
    async with semaphore:
        return await handler(batch)


async def process_in_batches(
    items: Iterable[T],
    handler: Callable[[List[T]], Awaitable[List[R]]],
    *,
    batch_size: int,
    concurrency: int,
) -> List[R]:
    """
    Splits items into batches and processes them concurrently with a limit.

    This function creates batches of `batch_size` from the `items` iterable.
    It then runs the asynchronous `handler` on each batch, ensuring that no
    more than `concurrency` handlers are running at any given time.

    The results from each batch are collected and flattened into a single list,
    maintaining the order corresponding to the original batches.

    Args:
        items: An iterable of items to process.
        handler: An async function that takes a batch (a list of items)
                 and returns a list of results.
        batch_size: The maximum number of items in each batch. Must be > 0.
        concurrency: The maximum number of concurrent handler calls. Must be > 0.

    Returns:
        A single list containing the flattened results from all batches,
        in the order of the original batches.

    Raises:
        ValueError: If `batch_size` or `concurrency` are not positive integers.
    """
    _validate_positive_integer(batch_size, "batch_size")
    _validate_positive_integer(concurrency, "concurrency")

    semaphore = asyncio.Semaphore(concurrency)

    tasks = [
        asyncio.create_task(
            _process_batch_with_semaphore(handler, batch, semaphore)
        )
        for batch in _create_batches(items, batch_size)
    ]

    # asyncio.gather collects results from the tasks, preserving their order.
    # If any handler raises an exception, gather will propagate it here.
    list_of_results = await asyncio.gather(*tasks)

    # Flatten the list of lists into a single list of results.
    return [item for sublist in list_of_results for item in sublist]
