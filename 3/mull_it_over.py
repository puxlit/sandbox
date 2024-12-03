#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable, Iterator
import re


########################################################################################################################
# Part 1
########################################################################################################################

UNCORRUPTED_MUL_PATTERN = re.compile(r'mul\((\d{1,3}),(\d{1,3})\)')


def extract_uncorrupted_muls(lines: Iterable[str]) -> Iterator[tuple[int, int]]:
    """
    >>> list(extract_uncorrupted_muls([
    ...     'mul(44,46)',
    ...     'mul(123,4)',
    ...     'mul(4*',
    ...     'mul(6,9!',
    ...     '?(12,34)',
    ...     'mul ( 2 , 4 )',
    ... ]))
    [(44, 46), (123, 4)]
    >>> list(extract_uncorrupted_muls([
    ...     'xmul(2,4)%&mul[3,7]!@^do_not_mul(5,5)+mul(32,64]then(mul(11,8)mul(8,5))',
    ... ]))
    [(2, 4), (5, 5), (11, 8), (8, 5)]
    """
    for line in lines:
        for match in UNCORRUPTED_MUL_PATTERN.finditer(line):
            (a, b) = match.groups()
            yield (int(a), int(b))


def sum_uncorrupted_muls(lines: Iterable[str]) -> int:
    """
    >>> sum_uncorrupted_muls([
    ...     'xmul(2,4)%&mul[3,7]!@^do_not_mul(5,5)+mul(32,64]then(mul(11,8)mul(8,5))',
    ... ])
    161
    """
    muls = extract_uncorrupted_muls(lines)
    return sum(a * b for (a, b) in muls)


########################################################################################################################
# CLI bootstrap
########################################################################################################################

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('part', type=int, choices=(1, 2))
    parser.add_argument('input', type=argparse.FileType('rt'))
    args = parser.parse_args()
    lines = (line.rstrip('\n') for line in args.input)

    if args.part == 1:
        print(sum_uncorrupted_muls(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
