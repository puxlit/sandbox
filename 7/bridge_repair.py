#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable, Iterator
from typing import NamedTuple


########################################################################################################################
# Equation
########################################################################################################################

class Equation(NamedTuple):
    test_value: int
    operands: tuple[int, ...]

    @classmethod
    def from_line(cls, line: str) -> 'Equation':
        (test_value, operands) = line.split(': ')
        return Equation(int(test_value), tuple(int(operand) for operand in operands.split()))


########################################################################################################################
# Part 1
########################################################################################################################

def parse_equations(lines: Iterable[str]) -> Iterator[Equation]:
    for line in lines:
        yield Equation.from_line(line)


def is_solvable_with_add_mul(goal: int, operands: tuple[int, ...]) -> bool:
    """
    >>> is_solvable_with_add_mul(190, (10, 19))
    True
    >>> is_solvable_with_add_mul(3267, (81, 40, 27))
    True
    >>> is_solvable_with_add_mul(292, (11, 6, 16, 20))
    True

    >>> is_solvable_with_add_mul(83, (17, 5))
    False
    >>> is_solvable_with_add_mul(156, (15, 6))
    False
    >>> is_solvable_with_add_mul(7290, (6, 8, 6, 15))
    False
    >>> is_solvable_with_add_mul(161011, (16, 10, 13))
    False
    >>> is_solvable_with_add_mul(192, (17, 8, 14))
    False
    >>> is_solvable_with_add_mul(21037, (9, 7, 18, 13))
    False

    >>> is_solvable_with_add_mul(49, (3, 14, 7))
    True
    """
    assert len(operands) >= 1
    for i in range(len(operands) - 1, 0, -1):
        operand = operands[i]
        (quotient, remainder) = divmod(goal, operand)
        if remainder == 0:
            if is_solvable_with_add_mul(goal - operand, operands[:i]):
                return True
            goal = quotient
        else:
            goal -= operand
    return goal == operands[0]


def sum_calibration_result(lines: Iterable[str]) -> int:
    """
    >>> sum_calibration_result([
    ...     '190: 10 19',
    ...     '3267: 81 40 27',
    ...     '83: 17 5',
    ...     '156: 15 6',
    ...     '7290: 6 8 6 15',
    ...     '161011: 16 10 13',
    ...     '192: 17 8 14',
    ...     '21037: 9 7 18 13',
    ...     '292: 11 6 16 20',
    ... ])
    3749
    """
    equations = parse_equations(lines)
    return sum(equation.test_value for equation in equations if is_solvable_with_add_and_mul(*equation))


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
        print(sum_calibration_result(lines))
    elif args.part == 1:
        print(sum_calibration_result_with_cat(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
