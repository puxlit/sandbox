#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable
from enum import Enum
from math import prod
import re
from typing import NamedTuple


########################################################################################################################
# Worksheet
########################################################################################################################

class Operation(Enum):
    ADD = '+'
    MULTIPLY = '*'


class Problem(NamedTuple):
    numbers: tuple[int, ...]
    operation: Operation

    def solve(self) -> int:
        """
        >>> Problem((123, 45, 6), Operation.MULTIPLY).solve()
        33210
        >>> Problem((328, 64, 98), Operation.ADD).solve()
        490
        >>> Problem((51, 387, 215), Operation.MULTIPLY).solve()
        4243455
        >>> Problem((64, 23, 314), Operation.ADD).solve()
        401
        """
        if self.operation == Operation.ADD:
            return sum(self.numbers)
        elif self.operation == Operation.MULTIPLY:
            return prod(self.numbers)
        else:
            raise ValueError(f'Unexpected operation: {self.operation!r}')


ASCII_DIGITS_PATTERN = re.compile(r'^[0-9]+$')


class Worksheet(NamedTuple):
    problems: tuple[Problem, ...]

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Worksheet':
        problem_numbers: list[list[int]] = []
        num_problems = -1
        for (y, line) in enumerate(lines):
            raw_columns = line.split()
            if (num_columns := len(raw_columns)) == 0:
                raise ValueError('Unexpected blank line')
            if y == 0:
                problem_numbers = [[] for _ in range(num_columns)]
                num_problems = num_columns
            elif num_columns != num_problems:
                raise ValueError(f'Number of columns on line {y + 1} differs from line 1 ({num_columns} ≠ {num_problems})')
            if ASCII_DIGITS_PATTERN.fullmatch(raw_columns[0]):
                for (x, raw_number) in enumerate(raw_columns):
                    problem_numbers[x].append(int(raw_number))
                continue
            break
        problem_operations = (Operation(raw_operation) for raw_operation in raw_columns)
        problems = tuple(Problem(tuple(numbers), operation) for (numbers, operation) in zip(problem_numbers, problem_operations))
        return Worksheet(problems)

    def sum_grand_total(self) -> int:
        """
        >>> Worksheet.from_lines([
        ...     '123 328  51 64 ',
        ...     ' 45 64  387 23 ',
        ...     '  6 98  215 314',
        ...     '*   +   *   +  ',
        ... ]).sum_grand_total()
        4277556
        """
        return sum(problem.solve() for problem in self.problems)


########################################################################################################################
# Part 1
########################################################################################################################

def sum_grand_total(lines: Iterable[str]) -> int:
    """
    >>> sum_grand_total([
    ...     '123 328  51 64 ',
    ...     ' 45 64  387 23 ',
    ...     '  6 98  215 314',
    ...     '*   +   *   +  ',
    ... ])
    4277556
    """
    return Worksheet.from_lines(lines).sum_grand_total()


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
        print(sum_grand_total(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
