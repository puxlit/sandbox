#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable


########################################################################################################################
# Part 1
########################################################################################################################

def parse_bank(line: str) -> tuple[int, ...]:
    return tuple(int(raw_battery_joltage) for raw_battery_joltage in line)


def find_safe_max_bank_joltage(bank: tuple[int, ...]) -> int:
    """
    >>> find_safe_max_bank_joltage((9, 8, 7, 6, 5, 4, 3, 2, 1, 1, 1, 1, 1, 1, 1))
    98
    >>> find_safe_max_bank_joltage((8, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 9))
    89
    >>> find_safe_max_bank_joltage((2, 3, 4, 2, 3, 4, 2, 3, 4, 2, 3, 4, 2, 7, 8))
    78
    >>> find_safe_max_bank_joltage((8, 1, 8, 1, 8, 1, 9, 1, 1, 1, 1, 2, 1, 1, 1))
    92
    """
    assert len(bank) >= 2
    # We reserve one battery at the end so we have at least one candidate for the least significant battery joltage.
    most_significant_battery_joltage = max(bank[:-1])
    start_index = bank.index(most_significant_battery_joltage) + 1
    least_significant_battery_joltage = max(bank[start_index:])
    return (most_significant_battery_joltage * 10) + least_significant_battery_joltage


def sum_max_safe_bank_joltages(lines: Iterable[str]) -> int:
    """
    >>> sum_max_safe_bank_joltages([
    ...     '987654321111111',
    ...     '811111111111119',
    ...     '234234234234278',
    ...     '818181911112111',
    ... ])
    357
    """
    banks = map(parse_bank, lines)
    return sum(find_safe_max_bank_joltage(bank) for bank in banks)


########################################################################################################################
# Part 2
########################################################################################################################

UNSAFE_BATTERIES_PER_BANK = 12


def find_max_bank_joltage(num_batteries: int, bank: tuple[int, ...]) -> int:
    """
    >>> find_max_bank_joltage(UNSAFE_BATTERIES_PER_BANK, (9, 8, 7, 6, 5, 4, 3, 2, 1, 1, 1, 1, 1, 1, 1))
    987654321111
    >>> find_max_bank_joltage(UNSAFE_BATTERIES_PER_BANK, (8, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 9))
    811111111119
    >>> find_max_bank_joltage(UNSAFE_BATTERIES_PER_BANK, (2, 3, 4, 2, 3, 4, 2, 3, 4, 2, 3, 4, 2, 7, 8))
    434234234278
    >>> find_max_bank_joltage(UNSAFE_BATTERIES_PER_BANK, (8, 1, 8, 1, 8, 1, 9, 1, 1, 1, 1, 2, 1, 1, 1))
    888911112111
    """
    assert 0 < num_batteries <= len(bank)

    if num_batteries == 1:
        return max(bank)

    num_remaining_batteries = num_batteries - 1
    # NB: Without the type hint, Mypy infers `multiplier` is `Any`.
    multiplier: int = 10 ** num_remaining_batteries
    battery_joltage = max(bank[:-num_remaining_batteries])
    start_index = bank.index(battery_joltage) + 1
    return (battery_joltage * multiplier) + find_max_bank_joltage(num_remaining_batteries, bank[start_index:])


def sum_max_unsafe_bank_joltages(lines: Iterable[str]) -> int:
    """
    >>> sum_max_unsafe_bank_joltages([
    ...     '987654321111111',
    ...     '811111111111119',
    ...     '234234234234278',
    ...     '818181911112111',
    ... ])
    3121910778619
    """
    banks = map(parse_bank, lines)
    return sum(find_max_bank_joltage(UNSAFE_BATTERIES_PER_BANK, bank) for bank in banks)


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
        print(sum_max_safe_bank_joltages(lines))
    elif args.part == 2:
        print(sum_max_unsafe_bank_joltages(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
