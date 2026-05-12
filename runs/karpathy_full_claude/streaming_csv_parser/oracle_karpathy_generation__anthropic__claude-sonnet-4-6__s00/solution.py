import csv


def parse_csv_rows(lines):
    non_empty = (line for line in lines if line.strip())
    reader = csv.DictReader(non_empty)
    yield from reader
