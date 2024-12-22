#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable, Iterator
from functools import partial


########################################################################################################################
# Monkey business
########################################################################################################################

STEP_ONE_LEFT_SHIFT = 6                # This is effectively a multiplier of         64.
STEP_TWO_RIGHT_SHIFT = 5               # This is effectively a divisor    of         32.
STEP_THREE_LEFT_SHIFT = 11             # This is effectively a multiplier of      2,048.
SECRET_NUMBER_BITMASK = (1 << 24) - 1  # This is effectively a modulus    of 16,777,216.


def parse_initial_secret_numbers(lines: Iterable[str]) -> Iterator[int]:
    return (int(line) for line in lines)


def next_secret_number(secret_number: int) -> int:
    """
    >>> secret_number = 123
    >>> tuple((secret_number := next_secret_number(secret_number)) for _ in range(10))
    (15887950, 16495136, 527345, 704524, 1553684, 12683156, 11100544, 12249484, 7753432, 5908254)
    """
    next_secret_number = ((secret_number << STEP_ONE_LEFT_SHIFT) ^ secret_number) & SECRET_NUMBER_BITMASK
    next_secret_number = ((next_secret_number >> STEP_TWO_RIGHT_SHIFT) ^ next_secret_number) & SECRET_NUMBER_BITMASK
    next_secret_number = ((next_secret_number << STEP_THREE_LEFT_SHIFT) ^ next_secret_number) & SECRET_NUMBER_BITMASK
    return next_secret_number


def nth_secret_number(secret_number: int, n: int) -> int:
    """
    >>> tuple(nth_secret_number(initial_secret_number, 2000) for initial_secret_number in (1, 10, 100, 2024))
    (8685429, 4700978, 15273692, 8667524)
    """
    assert n >= 0
    witnessed_secret_numbers = {secret_number}
    witnessed_secret_number_sequence = [secret_number]
    while n > 0:
        secret_number = next_secret_number(secret_number)
        if secret_number in witnessed_secret_numbers:
            break
        witnessed_secret_numbers.add(secret_number)
        witnessed_secret_number_sequence.append(secret_number)
        n -= 1
    if n == 0:
        return secret_number
    cycle_start_index = witnessed_secret_number_sequence.index(secret_number)
    cycle_length = len(witnessed_secret_number_sequence) - cycle_start_index
    return witnessed_secret_number_sequence[cycle_start_index + (n % cycle_length)]


########################################################################################################################
# Part 1
########################################################################################################################

def sum_two_thousandth_secret_numbers(lines: Iterable[str]) -> int:
    """
    >>> sum_two_thousandth_secret_numbers([
    ...     '1',
    ...     '10',
    ...     '100',
    ...     '2024',
    ... ])
    37327623
    """
    initial_secret_numbers = parse_initial_secret_numbers(lines)
    return sum(map(partial(nth_secret_number, n=2000), initial_secret_numbers))


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
        print(sum_two_thousandth_secret_numbers(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
