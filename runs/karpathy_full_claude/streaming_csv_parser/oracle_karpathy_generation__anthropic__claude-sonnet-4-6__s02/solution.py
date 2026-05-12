import csv


def parse_csv_rows(lines):
    non_empty = (line for line in lines if line.strip())
    reader = csv.DictReader(non_empty)
    # csv.DictReader reads the header lazily on first iteration
    # We need to feed it a proper iterable where first line is header
    # csv.DictReader treats first row as fieldnames by default
    yield from reader
