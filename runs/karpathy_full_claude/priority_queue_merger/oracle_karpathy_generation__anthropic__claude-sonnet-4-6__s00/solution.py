import heapq

def merge_sorted_iterators(iterators):
    heap = []
    iters = [iter(it) for it in iterators]
    for i, it in enumerate(iters):
        try:
            val = next(it)
            heapq.heappush(heap, (val, i, it))
        except StopIteration:
            pass
    while heap:
        val, i, it = heapq.heappop(heap)
        yield val
        try:
            next_val = next(it)
            heapq.heappush(heap, (next_val, i, it))
        except StopIteration:
            pass
