#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable
from enum import Enum
from itertools import chain
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

        >>> Problem((4, 431, 623), Operation.ADD).solve()
        1058
        >>> Problem((175, 581, 32), Operation.MULTIPLY).solve()
        3253600
        >>> Problem((8, 248, 369), Operation.ADD).solve()
        625
        >>> Problem((356, 24, 1), Operation.MULTIPLY).solve()
        8544
        """
        if self.operation == Operation.ADD:
            return sum(self.numbers)
        elif self.operation == Operation.MULTIPLY:
            return prod(self.numbers)
        else:
            raise ValueError(f'Unexpected operation: {self.operation!r}')


ASCII_DIGITS_PATTERN = re.compile(r'^[0-9]+$')
NUMBERS_LINE_PATTERN = re.compile(r'^ *[0-9]+ *(?: +[0-9]+ *)*$')
OPERATIONS_LINE_PATTERN = re.compile(r'^([*+] *)(?: ([*+] *))*$')


class Worksheet(NamedTuple):
    problems: tuple[Problem, ...]

    @classmethod
    def from_lines_incorrectly(cls, lines: Iterable[str]) -> 'Worksheet':
        """
        >>> Worksheet.from_lines_incorrectly([
        ...     '123 328  51 64 ',
        ...     ' 45 64  387 23 ',
        ...     '  6 98  215 314',
        ...     '*   +   *   +  ',
        ... ])
        Worksheet(problems=(Problem(numbers=(123, 45, 6), operation=<Operation.MULTIPLY: '*'>), Problem(numbers=(328, 64, 98), operation=<Operation.ADD: '+'>), Problem(numbers=(51, 387, 215), operation=<Operation.MULTIPLY: '*'>), Problem(numbers=(64, 23, 314), operation=<Operation.ADD: '+'>)))
        """
        problem_numbers: list[list[int]] = []
        num_problems = -1
        for (y, line) in enumerate(lines):
            raw_columns = line.split()
            if (num_columns := len(raw_columns)) == 0:
                raise ValueError(f'Unexpected end of input on line {y + 1}')
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

    @classmethod
    def from_lines_correctly(cls, lines: Iterable[str]) -> 'Worksheet':
        """
        >>> Worksheet.from_lines_correctly([
        ...     '123 328  51 64 ',
        ...     ' 45 64  387 23 ',
        ...     '  6 98  215 314',
        ...     '*   +   *   +  ',
        ... ])
        Worksheet(problems=(Problem(numbers=(4, 431, 623), operation=<Operation.ADD: '+'>), Problem(numbers=(175, 581, 32), operation=<Operation.MULTIPLY: '*'>), Problem(numbers=(8, 248, 369), operation=<Operation.ADD: '+'>), Problem(numbers=(356, 24, 1), operation=<Operation.MULTIPLY: '*'>)))
        """
        width = -1
        numbers_lines: list[str] = []
        for (y, line) in enumerate(lines):
            if y == 0:
                width = len(line)
            elif len(line) != width:
                raise ValueError(f'Width of line {y + 1} differs from line 1 ({len(line)} ≠ {width})')
            if NUMBERS_LINE_PATTERN.fullmatch(line):
                # Collect these to process later.
                numbers_lines.append(line)
                continue
            if OPERATIONS_LINE_PATTERN.fullmatch(line):
                break
            raise ValueError(f'Unexpected contents on line {y + 1}: {line!r}')

        # Part one: collect operations and field widths.
        num_problems = 0
        problem_operations: list[Operation] = []
        problem_num_numbers: list[int] = []
        gutter_indices: list[int] = []
        for (x, char) in enumerate(line):
            if char == ' ':
                problem_num_numbers[-1] += 1
            else:
                if num_problems:
                    assert problem_num_numbers[-1] > 1
                    problem_num_numbers[-1] -= 1
                    gutter_indices.append(x - 1)
                num_problems += 1
                problem_operations.append(Operation(char))
                problem_num_numbers.append(1)
        assert len(problem_operations) == len(problem_num_numbers) == len(gutter_indices) + 1 == num_problems >= 1
        assert all(digits >= 1 for digits in problem_num_numbers)

        # Part two: collect numbers.
        problem_numbers: list[list[int]] = [([0] * problem_num_numbers[i]) for i in range(num_problems)]
        problem_numbers_finalised: list[list[bool]] = [([False] * problem_num_numbers[i]) for i in range(num_problems)]
        for line in numbers_lines:
            assert all(line[x] == ' ' for x in gutter_indices)
            for (i, x) in enumerate(chain(gutter_indices, [width])):
                for j in range(problem_num_numbers[i]):
                    x -= 1
                    if (char := line[x]) == ' ':
                        if problem_numbers[i][j] != 0:
                            problem_numbers_finalised[i][j] = True
                    else:
                        assert problem_numbers[i][j] == 0 or not problem_numbers_finalised[i][j]
                        digit = int(char)
                        problem_numbers[i][j] = (problem_numbers[i][j] * 10) + digit
        assert all(
            number > 0
            for numbers in problem_numbers
            for number in numbers
        )

        problems = tuple(
            Problem(tuple(numbers), operations)
            for (numbers, operations) in zip(reversed(problem_numbers), reversed(problem_operations))
        )
        return Worksheet(problems)

    def sum_grand_total(self) -> int:
        """
        >>> Worksheet.from_lines_incorrectly([
        ...     '123 328  51 64 ',
        ...     ' 45 64  387 23 ',
        ...     '  6 98  215 314',
        ...     '*   +   *   +  ',
        ... ]).sum_grand_total()
        4277556

        >>> Worksheet.from_lines_correctly([
        ...     '123 328  51 64 ',
        ...     ' 45 64  387 23 ',
        ...     '  6 98  215 314',
        ...     '*   +   *   +  ',
        ... ]).sum_grand_total()
        3263827
        """
        return sum(problem.solve() for problem in self.problems)


########################################################################################################################
# Part 1
########################################################################################################################

def sum_grand_total_incorrectly(lines: Iterable[str]) -> int:
    """
    >>> sum_grand_total_incorrectly([
    ...     '123 328  51 64 ',
    ...     ' 45 64  387 23 ',
    ...     '  6 98  215 314',
    ...     '*   +   *   +  ',
    ... ])
    4277556
    """
    return Worksheet.from_lines_incorrectly(lines).sum_grand_total()


########################################################################################################################
# Part 2
########################################################################################################################

def sum_grand_total_correctly(lines: Iterable[str]) -> int:
    """
    >>> sum_grand_total_correctly([
    ...     '123 328  51 64 ',
    ...     ' 45 64  387 23 ',
    ...     '  6 98  215 314',
    ...     '*   +   *   +  ',
    ... ])
    3263827
    """
    return Worksheet.from_lines_correctly(lines).sum_grand_total()


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
        print(sum_grand_total_incorrectly(lines))
    elif args.part == 2:
        print(sum_grand_total_correctly(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
