#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable, Iterator
from typing import NamedTuple, Optional


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
    num_operands = len(operands)
    assert num_operands >= 1

    if num_operands == 1:
        return goal == operands[0]

    operand = operands[-1]
    remaining_operands = operands[:-1]

    (quotient, remainder) = divmod(goal, operand)
    if remainder == 0:
        if is_solvable_with_add_mul(quotient, remaining_operands):
            return True

    return is_solvable_with_add_mul(goal - operand, remaining_operands)


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
    return sum(equation.test_value for equation in equations if is_solvable_with_add_mul(*equation))


########################################################################################################################
# Part 2
########################################################################################################################

def chomp(value: int, suffix: int) -> Optional[int]:
    """
    >>> chomp(156, 6)
    15
    >>> chomp(7290, 90)
    72
    >>> chomp(1230, 0)
    123
    >>> chomp(1234, 0) is None
    True
    >>> chomp(123, 4) is None
    True
    """
    while True:
        (suffix_significant_digits, suffix_units_digit) = divmod(suffix, 10)
        (value_quotient, value_remainder) = divmod(value - suffix_units_digit, 10)
        if value_remainder != 0:
            return None
        suffix = suffix_significant_digits
        value = value_quotient
        if suffix == 0:
            break
    return value


def is_solvable_with_add_mul_cat(goal: int, operands: tuple[int, ...]) -> bool:
    """
    >>> is_solvable_with_add_mul_cat(156, (15, 6))
    True
    >>> is_solvable_with_add_mul_cat(7290, (6, 8, 6, 15))
    True
    >>> is_solvable_with_add_mul_cat(192, (17, 8, 14))
    True

    >>> is_solvable_with_add_mul_cat(190, (10, 19))
    True
    >>> is_solvable_with_add_mul_cat(3267, (81, 40, 27))
    True
    >>> is_solvable_with_add_mul_cat(292, (11, 6, 16, 20))
    True

    >>> is_solvable_with_add_mul_cat(83, (17, 5))
    False
    >>> is_solvable_with_add_mul_cat(161011, (16, 10, 13))
    False
    >>> is_solvable_with_add_mul_cat(21037, (9, 7, 18, 13))
    False

    >>> is_solvable_with_add_mul_cat(49, (3, 14, 7))
    True
    """
    num_operands = len(operands)
    assert num_operands >= 1

    if num_operands == 1:
        return goal == operands[0]

    operand = operands[-1]
    remaining_operands = operands[:-1]

    prefix = chomp(goal, operand)
    if prefix is not None:
        if is_solvable_with_add_mul_cat(prefix, remaining_operands):
            return True

    (quotient, remainder) = divmod(goal, operand)
    if remainder == 0:
        if is_solvable_with_add_mul_cat(quotient, remaining_operands):
            return True

    return is_solvable_with_add_mul_cat(goal - operand, remaining_operands)


def sum_calibration_result_with_cat(lines: Iterable[str]) -> int:
    """
    >>> sum_calibration_result_with_cat([
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
    11387
    """
    equations = parse_equations(lines)
    return sum(equation.test_value for equation in equations if is_solvable_with_add_mul_cat(*equation))


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
    elif args.part == 2:
        print(sum_calibration_result_with_cat(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
