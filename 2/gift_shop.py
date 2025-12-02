#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable, Iterator
from math import log10


########################################################################################################################
# Part 1
########################################################################################################################

RANGE_DELIMITER = ','
BOUND_DELIMITER = '-'


def parse_bounds(line: str) -> Iterator[tuple[int, int]]:
    """
    >>> list(parse_bounds('11-22,95-115,998-1012,1188511880-1188511890,222220-222224,1698522-1698528,446443-446449,38593856-38593862,565653-565659,824824821-824824827,2121212118-2121212124'))
    [(11, 22), (95, 115), (998, 1012), (1188511880, 1188511890), (222220, 222224), (1698522, 1698528), (446443, 446449), (38593856, 38593862), (565653, 565659), (824824821, 824824827), (2121212118, 2121212124)]
    """
    for raw_bound in line.split(RANGE_DELIMITER):
        (lower_bound, upper_bound) = map(int, raw_bound.split(BOUND_DELIMITER))
        if lower_bound > upper_bound:
            raise ValueError(f'Invalid bound: {lower_bound} ≰ {upper_bound}')
        if lower_bound < 1:
            raise ValueError(f'Invalid bound: 1 ≰ {lower_bound} ≤ {upper_bound}')
        yield (lower_bound, upper_bound)


def count_digits(number: int) -> int:
    assert number > 0
    return int(log10(number)) + 1


def enumerate_invalid_product_ids(lower_bound: int, upper_bound: int) -> Iterator[int]:
    """
    >>> list(enumerate_invalid_product_ids(55, 55))
    [55]
    >>> list(enumerate_invalid_product_ids(6464, 6464))
    [6464]
    >>> list(enumerate_invalid_product_ids(123123, 123123))
    [123123]

    >>> list(enumerate_invalid_product_ids(11, 22))
    [11, 22]
    >>> list(enumerate_invalid_product_ids(95, 115))
    [99]
    >>> list(enumerate_invalid_product_ids(998, 1012))
    [1010]
    >>> list(enumerate_invalid_product_ids(1188511880, 1188511890))
    [1188511885]
    >>> list(enumerate_invalid_product_ids(222220, 222224))
    [222222]
    >>> list(enumerate_invalid_product_ids(1698522, 1698528))
    []
    >>> list(enumerate_invalid_product_ids(446443, 446449))
    [446446]
    >>> list(enumerate_invalid_product_ids(38593856, 38593862))
    [38593859]
    >>> list(enumerate_invalid_product_ids(565653, 565659))
    []
    >>> list(enumerate_invalid_product_ids(824824821, 824824827))
    []
    >>> list(enumerate_invalid_product_ids(2121212118, 2121212124))
    []
    """
    assert 1 <= lower_bound <= upper_bound

    lower_bound_digits = count_digits(lower_bound)
    if lower_bound_digits % 2 == 0:
        # For example, the lower piece bound for 67 is 6.
        (lower_piece_bound, remainder) = divmod(lower_bound, (10 ** (lower_bound_digits // 2)))
        if lower_piece_bound < remainder:
            # For example, the lower piece bound for 565653 is 566.
            lower_piece_bound += 1
    else:
        # For example, the lower piece bound for 998 is 10.
        lower_piece_bound = 10 ** (lower_bound_digits // 2)

    upper_bound_digits = count_digits(upper_bound)
    if upper_bound_digits % 2 == 0:
        # For example, the upper piece bound for 987999 is 987.
        (upper_piece_bound, remainder) = divmod(upper_bound, 10 ** (upper_bound_digits // 2))
        if upper_piece_bound > remainder:
            # For example, the upper piece bound for 987654 is 986.
            upper_piece_bound -= 1
    else:
        # For example, the upper piece bound for 12345 is 99.
        upper_piece_bound = (10 ** (upper_bound_digits // 2)) - 1

    for piece in range(lower_piece_bound, upper_piece_bound + 1):
        piece_digits = count_digits(piece)
        invalid_product_id = (piece * (10 ** piece_digits)) + piece
        assert lower_bound <= invalid_product_id <= upper_bound
        yield invalid_product_id


def sum_invalid_product_ids(lines: Iterable[str]) -> int:
    """
    >>> sum_invalid_product_ids(['11-22,95-115,998-1012,1188511880-1188511890,222220-222224,1698522-1698528,446443-446449,38593856-38593862,565653-565659,824824821-824824827,2121212118-2121212124'])
    1227775554
    """
    bounds = parse_bounds(next(iter(lines)))
    return sum(
        invalid_product_id
        for bound in bounds
        for invalid_product_id in enumerate_invalid_product_ids(*bound)
    )


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
        print(sum_invalid_product_ids(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
