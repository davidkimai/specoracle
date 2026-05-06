import csv


def parse_csv_rows(lines, normalize_header=None):
    """
    Parse CSV rows from an iterable of strings.
    
    The first non-empty line is treated as the header row.
    Each subsequent non-empty line is yielded as a dict mapping header names to cell values.
    
    Args:
        lines: An iterable of strings representing CSV lines.
        normalize_header: An optional callable applied to each header cell before
                          building row dictionaries. When None, headers are used as-is.
        
    Yields:
        dict[str, str]: A dictionary mapping header field names to cell values.
    """
    def non_empty_lines(iterable):
        for line in iterable:
            stripped = line.rstrip('\n').rstrip('\r')
            if stripped.strip():
                yield stripped

    filtered = non_empty_lines(lines)

    reader = csv.DictReader(filtered)

    if normalize_header is not None:
        # Access fieldnames to trigger header parsing, then remap
        original_fieldnames = reader.fieldnames
        if original_fieldnames is not None:
            reader.fieldnames = [normalize_header(f) for f in original_fieldnames]

    for row in reader:
        yield dict(row)
