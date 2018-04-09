"""
Reads a CSV file containing an exported legacy table
as a list of dicts mapping column names to string values
"""
from csv import reader


def read_csv(table_name):
    with open(table_name + '.csv', encoding='latin-1') as csv_file:
        headers = None
        for row in reader(csv_file):
            if headers is None:
                headers = row
                continue
            row_dict = {}
            for k, v in zip(headers, row):
                row_dict[k] = v
            yield row_dict
