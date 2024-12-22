#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable, Iterator
from functools import partial
from itertools import islice


########################################################################################################################
# Monkey business
########################################################################################################################

TOTAL_DELTA_VALUES = 19                                  # Delta values range from -9 to 9 (inclusive).
DELTA_VALUE_TO_INDEX_OFFSET = 9
TOTAL_DELTA_SEQUENCE_COUNTERS = TOTAL_DELTA_VALUES ** 4  # 19⁴ = 130,321.
MAX_NEW_SECRET_NUMBERS = 2000

STEP_ONE_BITMASK = (1 << 18) - 1    # This bitmask ensures that the result (post-left shift) remains 24-bit.
STEP_ONE_LEFT_SHIFT = 6             # This is effectively a multiplier of         64.
STEP_TWO_RIGHT_SHIFT = 5            # This is effectively a divisor    of         32.
STEP_THREE_BITMASK = (1 << 13) - 1  # This bitmask ensures that the result (post-left shift) remains 24-bit.
STEP_THREE_LEFT_SHIFT = 11          # This is effectively a multiplier of      2,048.
MAX_SECRET_NUMBER = (1 << 24) - 1   # This is effectively a modulus    of 16,777,216.


def parse_initial_secret_numbers(lines: Iterable[str]) -> Iterator[int]:
    for line in lines:
        assert 0 <= (initial_secret_number := int(line)) <= MAX_SECRET_NUMBER
        yield initial_secret_number


def next_secret_number(secret_number: int) -> int:
    # We'll assume `secret_number` is a valid 24-bit unsigned integer.
    next_secret_number = ((secret_number & STEP_ONE_BITMASK) << STEP_ONE_LEFT_SHIFT) ^ secret_number
    next_secret_number = (next_secret_number >> STEP_TWO_RIGHT_SHIFT) ^ next_secret_number
    next_secret_number = ((next_secret_number & STEP_THREE_BITMASK) << STEP_THREE_LEFT_SHIFT) ^ next_secret_number
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
    max_delta_sequence_sales = 0
    delta_sequence_sales = [0] * TOTAL_DELTA_SEQUENCE_COUNTERS
    initial_secret_numbers = parse_initial_secret_numbers(lines)
    for initial_secret_number in initial_secret_numbers:
        witnessed_delta_sequence_ids: set[int] = set()
        secret_numbers_iter = islice(secret_numbers(initial_secret_number), MAX_NEW_SECRET_NUMBERS)
        # Prime first delta.
        prev_price = initial_secret_number % 10
        price = next(secret_numbers_iter) % 10
        delta_i = ((price - prev_price) + DELTA_VALUE_TO_INDEX_OFFSET) * (TOTAL_DELTA_VALUES ** 3)
        prev_price = price
        # Prime second delta.
        price = next(secret_numbers_iter) % 10
        delta_j = ((price - prev_price) + DELTA_VALUE_TO_INDEX_OFFSET) * (TOTAL_DELTA_VALUES ** 2)
        prev_price = price
        # Prime third delta.
        price = next(secret_numbers_iter) % 10
        delta_k = ((price - prev_price) + DELTA_VALUE_TO_INDEX_OFFSET) * TOTAL_DELTA_VALUES
        prev_price = price
        # We're all primed. Next delta gives us a full delta sequence.
        for secret_number in secret_numbers_iter:
            price = secret_number % 10
            delta_l = (price - prev_price) + DELTA_VALUE_TO_INDEX_OFFSET
            delta_sequence_id = delta_i + delta_j + delta_k + delta_l
            if delta_sequence_id not in witnessed_delta_sequence_ids:
                witnessed_delta_sequence_ids.add(delta_sequence_id)
                if price != 0:
                    delta_sequence_sales[delta_sequence_id] += price
                    if delta_sequence_sales[delta_sequence_id] > max_delta_sequence_sales:
                        max_delta_sequence_sales = delta_sequence_sales[delta_sequence_id]
            prev_price = price
            delta_i = delta_j * TOTAL_DELTA_VALUES
            delta_j = delta_k * TOTAL_DELTA_VALUES
            delta_k = delta_l * TOTAL_DELTA_VALUES
    return max_delta_sequence_sales


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
