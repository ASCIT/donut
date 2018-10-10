#!/usr/bin/env python
import sys

filename = sys.argv[1]
with open(filename) as f:
    headers = None
    for line in f:
        if line[-1] == '\n': line = line[:-1]
        cols = line.split('\t')
        if not headers:
            headers = cols
            continue
        row = dict(zip(headers, cols))
