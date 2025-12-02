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
    lower_piece_divisor = 10 ** (lower_bound_digits // 2)
    if lower_bound_digits % 2 == 0:
        # For example, the lower piece bound for 67 is 6.
        (lower_piece_bound, remainder) = divmod(lower_bound, lower_piece_divisor)
        if lower_piece_bound < remainder:
            # For example, the lower piece bound for 565653 is 566.
            lower_piece_bound += 1
    else:
        # For example, the lower piece bound for 998 is 10.
        lower_piece_bound = lower_piece_divisor

    upper_bound_digits = count_digits(upper_bound)
    upper_piece_divisor = 10 ** (upper_bound_digits // 2)
    if upper_bound_digits % 2 == 0:
        # For example, the upper piece bound for 987999 is 987.
        (upper_piece_bound, remainder) = divmod(upper_bound, upper_piece_divisor)
        if upper_piece_bound > remainder:
            # For example, the upper piece bound for 987654 is 986.
            upper_piece_bound -= 1
    else:
        # For example, the upper piece bound for 12345 is 99.
        upper_piece_bound = upper_piece_divisor - 1

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
# Part 2
########################################################################################################################

def simplify_bounds(lower_bound: int, upper_bound: int) -> Iterator[tuple[int, int]]:
    """
    >>> list(simplify_bounds(11, 22))
    [(11, 22)]
    >>> list(simplify_bounds(95, 115))
    [(95, 99), (100, 115)]
    >>> list(simplify_bounds(95, 1215))
    [(95, 99), (100, 999), (1000, 1215)]
    """
    assert 1 <= lower_bound <= upper_bound

    lower_bound_digits = count_digits(lower_bound)
    upper_bound_digits = count_digits(upper_bound)
    if lower_bound_digits == upper_bound_digits:
        yield (lower_bound, upper_bound)
        return

    yield (lower_bound, (10 ** lower_bound_digits) - 1)
    for interstitial_bound_digits in range(lower_bound_digits + 1, upper_bound_digits):
        yield (10 ** (interstitial_bound_digits - 1), (10 ** interstitial_bound_digits) - 1)
    yield (10 ** (upper_bound_digits - 1), upper_bound)


def enumerate_extended_invalid_product_ids(lower_bound: int, upper_bound: int) -> Iterator[int]:
    """
    >>> list(enumerate_extended_invalid_product_ids(12341234, 12341234))
    [12341234]
    >>> list(enumerate_extended_invalid_product_ids(123123123, 123123123))
    [123123123]
    >>> list(enumerate_extended_invalid_product_ids(1212121212, 1212121212))
    [1212121212]
    >>> list(enumerate_extended_invalid_product_ids(1111111, 1111111))
    [1111111]

    >>> list(enumerate_extended_invalid_product_ids(11, 22))
    [11, 22]
    >>> list(enumerate_extended_invalid_product_ids(95, 99))
    [99]
    >>> list(enumerate_extended_invalid_product_ids(100, 115))
    [111]
    >>> list(enumerate_extended_invalid_product_ids(998, 999))
    [999]
    >>> list(enumerate_extended_invalid_product_ids(1000, 1012))
    [1010]
    >>> list(enumerate_extended_invalid_product_ids(1188511880, 1188511890))
    [1188511885]
    >>> list(enumerate_extended_invalid_product_ids(222220, 222224))
    [222222]
    >>> list(enumerate_extended_invalid_product_ids(1698522, 1698528))
    []
    >>> list(enumerate_extended_invalid_product_ids(446443, 446449))
    [446446]
    >>> list(enumerate_extended_invalid_product_ids(38593856, 38593862))
    [38593859]
    >>> list(enumerate_extended_invalid_product_ids(565653, 565659))
    [565656]
    >>> list(enumerate_extended_invalid_product_ids(824824821, 824824827))
    [824824824]
    >>> list(enumerate_extended_invalid_product_ids(2121212118, 2121212124))
    [2121212121]

    >>> sorted(enumerate_extended_invalid_product_ids(1000, 2222))
    [1010, 1111, 1212, 1313, 1414, 1515, 1616, 1717, 1818, 1919, 2020, 2121, 2222]
    """
    assert 1 <= lower_bound <= upper_bound

    bound_digits = count_digits(lower_bound)
    assert bound_digits == count_digits(upper_bound)

    witnessed_invalid_product_id: set[int] = set()
    for piece_digits in range(1, (bound_digits // 2) + 1):
        (num_pieces, remainder) = divmod(bound_digits, piece_digits)
        assert num_pieces > 0
        if remainder:
            # For example, we can't do two-digit pieces for 1234567.
            continue
        piece_divisor = 10 ** piece_digits

        lower_piece_bound = max(10 ** (piece_digits - 1), lower_bound // (10 ** (bound_digits - piece_digits)))
        upper_piece_bound = min(piece_divisor - 1, upper_bound % piece_divisor)

        for piece in range(lower_piece_bound, upper_piece_bound + 1):
            invalid_product_id = piece
            for _ in range(num_pieces - 1):
                invalid_product_id = (invalid_product_id * piece_divisor) + piece
            # TODO: Can we improve filtering further and turn this into an assertion?
            if lower_bound <= invalid_product_id <= upper_bound:
                if invalid_product_id not in witnessed_invalid_product_id:
                    yield invalid_product_id
                    witnessed_invalid_product_id.add(invalid_product_id)


def sum_extended_invalid_product_ids(lines: Iterable[str]) -> int:
    """
    >>> sum_extended_invalid_product_ids(['11-22,95-115,998-1012,1188511880-1188511890,222220-222224,1698522-1698528,446443-446449,38593856-38593862,565653-565659,824824821-824824827,2121212118-2121212124'])
    4174379265
    """
    bounds = parse_bounds(next(iter(lines)))
    return sum(
        invalid_product_id
        for bound in bounds
        for simplified_bounds in simplify_bounds(*bound)
        for invalid_product_id in enumerate_extended_invalid_product_ids(*simplified_bounds)
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
    elif args.part == 2:
        print(sum_extended_invalid_product_ids(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
