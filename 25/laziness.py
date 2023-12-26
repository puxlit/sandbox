#!/usr/bin/env python3


import sys
from typing import Optional


lines = (line.rstrip('\n') for line in sys.stdin)
prev_number: Optional[int] = None
max_delta = 0
first_set_size = 0
for (i, line) in enumerate(lines):
    number = int(line)
    if prev_number is not None:
        delta = number - prev_number
        if delta > max_delta:
            max_delta = delta
            first_set_size = i
    prev_number = number
print(first_set_size * (i + 1 - first_set_size))
