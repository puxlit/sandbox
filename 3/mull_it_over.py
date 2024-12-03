#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable, Iterator
import re
from typing import Union


########################################################################################################################
# Part 1
########################################################################################################################

MUL_PATTERN = re.compile(r'mul\((\d{1,3}),(\d{1,3})\)')


def extract_muls(lines: Iterable[str]) -> Iterator[tuple[int, int]]:
    """
    >>> list(extract_muls([
    ...     'mul(44,46)',
    ...     'mul(123,4)',
    ...     'mul(4*',
    ...     'mul(6,9!',
    ...     '?(12,34)',
    ...     'mul ( 2 , 4 )',
    ... ]))
    [(44, 46), (123, 4)]
    >>> list(extract_muls([
    ...     'xmul(2,4)%&mul[3,7]!@^do_not_mul(5,5)+mul(32,64]then(mul(11,8)mul(8,5))',
    ... ]))
    [(2, 4), (5, 5), (11, 8), (8, 5)]
    """
    for line in lines:
        for match in MUL_PATTERN.finditer(line):
            (a, b) = match.groups()
            yield (int(a), int(b))


def sum_muls(lines: Iterable[str]) -> int:
    """
    >>> sum_muls([
    ...     'xmul(2,4)%&mul[3,7]!@^do_not_mul(5,5)+mul(32,64]then(mul(11,8)mul(8,5))',
    ... ])
    161
    """
    muls = extract_muls(lines)
    return sum(a * b for (a, b) in muls)


########################################################################################################################
# Part 2
########################################################################################################################

OP_PATTERN = re.compile(r"(mul\((\d{1,3}),(\d{1,3})\)|do\(\)|don't\(\))")


def extract_ops(lines: Iterable[str]) -> Iterator[Union[bool, tuple[int, int]]]:
    """
    >>> list(extract_ops([
    ...     "xmul(2,4)&mul[3,7]!^don't()_mul(5,5)+mul(32,64](mul(11,8)undo()?mul(8,5))",
    ... ]))
    [(2, 4), False, (5, 5), (11, 8), True, (8, 5)]
    """
    for line in lines:
        for match in OP_PATTERN.finditer(line):
            (instruction, a, b) = match.groups()
            if instruction == 'do()':
                yield True
            elif instruction == 'don\'t()':
                yield False
            else:
                yield (int(a), int(b))


def execute_ops(ops: Iterable[Union[bool, tuple[int, int]]]) -> Iterator[int]:
    """
    >>> list(execute_ops([
    ...     (2, 4),
    ...     False,
    ...     (5, 5),
    ...     (11, 8),
    ...     True,
    ...     (8, 5),
    ... ]))
    [8, 40]
    """
    muls_enabled = True
    for op in ops:
        if isinstance(op, bool):
            muls_enabled = op
        else:
            if muls_enabled:
                (a, b) = op
                yield a * b


def sum_conditional_muls(lines: Iterable[str]) -> int:
    """
    >>> sum_conditional_muls([
    ...     "xmul(2,4)&mul[3,7]!^don't()_mul(5,5)+mul(32,64](mul(11,8)undo()?mul(8,5))",
    ... ])
    48
    """
    return sum(execute_ops(extract_ops(lines)))


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
        print(sum_muls(lines))
    elif args.part == 2:
        print(sum_conditional_muls(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
