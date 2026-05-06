import csv


def parse_csv_rows(lines):
    """
    Parse CSV rows from an iterable of strings.
    
    The first non-empty line is treated as the header row.
    Each subsequent non-empty line is yielded as a dict mapping header names to cell values.
    
    Args:
        lines: An iterable of strings representing CSV lines.
        
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
    
    # We need to handle the header manually to preserve streaming behavior
    # csv.DictReader reads the first row as fieldnames lazily
    for row in reader:
        yield dict(row)
