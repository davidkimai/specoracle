from __future__ import annotations


def merge_logs(streams: list, detect_gaps: bool = False):
    seen = set()
    merged = []
    for stream in streams:
        for record in stream:
            key = (record.get('source'), record.get('seq'))
            if key in seen:
                continue
            seen.add(key)
            merged.append(dict(record))

    sorted_records = sorted(merged, key=lambda row: row.get('ts', 0))

    if not detect_gaps:
        return sorted_records

    # Build per-source set of observed sequence numbers
    source_seqs: dict[str, list[int]] = {}
    for record in merged:
        source = record.get('source')
        seq = record.get('seq')
        if source is None or seq is None:
            continue
        source_seqs.setdefault(source, []).append(seq)

    gaps = []
    for source, seqs in source_seqs.items():
        min_seq = min(seqs)
        max_seq = max(seqs)
        observed = set(seqs)
        for missing_seq in range(min_seq, max_seq + 1):
            if missing_seq not in observed:
                gaps.append({'source': source, 'missing_seq': missing_seq})

    return sorted_records, gaps
