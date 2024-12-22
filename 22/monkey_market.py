#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections import Counter, deque
from collections.abc import Iterable, Iterator
from functools import partial
from itertools import islice


########################################################################################################################
# Monkey business
########################################################################################################################

MAX_NEW_SECRET_NUMBERS = 2000

STEP_ONE_LEFT_SHIFT = 6                # This is effectively a multiplier of         64.
STEP_TWO_RIGHT_SHIFT = 5               # This is effectively a divisor    of         32.
STEP_THREE_LEFT_SHIFT = 11             # This is effectively a multiplier of      2,048.
SECRET_NUMBER_BITMASK = (1 << 24) - 1  # This is effectively a modulus    of 16,777,216.


def parse_initial_secret_numbers(lines: Iterable[str]) -> Iterator[int]:
    return (int(line) for line in lines)


def next_secret_number(secret_number: int) -> int:
    next_secret_number = ((secret_number << STEP_ONE_LEFT_SHIFT) ^ secret_number) & SECRET_NUMBER_BITMASK
    next_secret_number = ((next_secret_number >> STEP_TWO_RIGHT_SHIFT) ^ next_secret_number) & SECRET_NUMBER_BITMASK
    next_secret_number = ((next_secret_number << STEP_THREE_LEFT_SHIFT) ^ next_secret_number) & SECRET_NUMBER_BITMASK
    return next_secret_number


def secret_numbers(secret_number: int) -> Iterator[int]:
    """
    >>> tuple(islice(secret_numbers(123), 10))
    (15887950, 16495136, 527345, 704524, 1553684, 12683156, 11100544, 12249484, 7753432, 5908254)
    """
    while True:
        yield (secret_number := next_secret_number(secret_number))


def nth_secret_number(secret_number: int, n: int) -> int:
    """
    >>> tuple(nth_secret_number(initial_secret_number, MAX_NEW_SECRET_NUMBERS) for initial_secret_number in (1, 10, 100, 2024))
    (8685429, 4700978, 15273692, 8667524)
    """
    assert n >= 0
    while n > 0:
        secret_number = next_secret_number(secret_number)
        n -= 1
    return secret_number


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
    return sum(map(partial(nth_secret_number, n=MAX_NEW_SECRET_NUMBERS), initial_secret_numbers))


########################################################################################################################
# Part 2
########################################################################################################################

def calculate_max_banana_sales(lines: Iterable[str]) -> int:
    """
    >>> calculate_max_banana_sales([
    ...     '1',
    ...     '2',
    ...     '3',
    ...     '2024',
    ... ])
    23
    """
    # Each delta can have a value from -9 to 9, so the total number of possible delta sequences is 19⁴ = 130,321.
    delta_sequence_sales: Counter[tuple[int, int, int, int]] = Counter()
    initial_secret_numbers = parse_initial_secret_numbers(lines)
    for initial_secret_number in initial_secret_numbers:
        prev_price = initial_secret_number % 10
        mutable_delta_sequence: deque[int] = deque(maxlen=4)
        witnessed_delta_sequences: set[tuple[int, int, int, int]] = set()
        for secret_number in islice(secret_numbers(initial_secret_number), MAX_NEW_SECRET_NUMBERS):
            price = secret_number % 10
            delta = price - prev_price
            mutable_delta_sequence.append(delta)
            if len(mutable_delta_sequence) == 4:
                # Mypy understandably isn't convinced that `tuple(mutable_delta_sequence)` has the type `tuple[int, int, int, int]`.
                delta_sequence = (mutable_delta_sequence[0], mutable_delta_sequence[1], mutable_delta_sequence[2], mutable_delta_sequence[3])
                if delta_sequence not in witnessed_delta_sequences:
                    delta_sequence_sales[delta_sequence] += price
                    witnessed_delta_sequences.add(delta_sequence)
            prev_price = price
    return max(delta_sequence_sales.values())


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
    elif args.part == 2:
        print(calculate_max_banana_sales(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
