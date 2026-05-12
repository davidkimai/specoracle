def merge_logs(streams):
    seen = set()
    result = []
    for stream in streams:
        for record in stream:
            key = (record["source"], record["seq"])
            if key not in seen:
                seen.add(key)
                result.append(dict(record))
    result.sort(key=lambda r: r["ts"])
    return result
