#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from bisect import bisect_left, bisect_right
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from functools import reduce
from typing import Any


########################################################################################################################
# Inventory management system
########################################################################################################################

BOUND_DELIMITER = '-'


@dataclass(frozen=True)
class Range:
    """
    Represent a closed integer interval.
    """
    lower_bound: int
    upper_bound: int
    overlaps: int

    @classmethod
    def from_line(cls, line: str) -> 'Range':
        (lower_bound, upper_bound) = map(int, line.split(BOUND_DELIMITER))
        return Range(lower_bound, upper_bound, 1)

    def __post_init__(self) -> None:
        """
        >>> Range(1, 2, 1)
        Range(lower_bound=1, upper_bound=2, overlaps=1)
        >>> Range(1, 1, 1)
        Range(lower_bound=1, upper_bound=1, overlaps=1)
        >>> Range(2, 1, 1)
        Traceback (most recent call last):
            ...
        ValueError: Invalid range: 2 ≰ 1
        >>> Range(1, 1, 0)
        Traceback (most recent call last):
            ...
        ValueError: Invalid overlap count: 0 ≯ 0
        """
        if self.lower_bound > self.upper_bound:
            raise ValueError(f'Invalid range: {self.lower_bound} ≰ {self.upper_bound}')
        if self.overlaps <= 0:
            raise ValueError(f'Invalid overlap count: {self.overlaps} ≯ 0')

    def __eq__(self, other: Any) -> bool:
        """
        >>> list(Range(2, 4, 1) == x for x in range(1, 6))
        [False, True, True, True, False]
        >>> Range(2, 4, 1) == 'a'
        Traceback (most recent call last):
            ...
        TypeError: Cannot evaluate `Range(lower_bound=2, upper_bound=4, overlaps=1) == 'a'`
        """
        if isinstance(other, int):
            return self.lower_bound <= other <= self.upper_bound
        raise TypeError(f'Cannot evaluate `{self!r} == {other!r}`')

    def __lt__(self, other: Any) -> bool:
        """
        >>> Range(1, 3, 1) < 4
        True
        >>> Range(1, 3, 1) < 3
        False
        >>> Range(1, 3, 1) < 2
        False
        >>> Range(1, 3, 1) < 1
        False
        >>> Range(1, 3, 1) < 0
        False
        """
        if isinstance(other, int):
            return self.upper_bound < other
        raise TypeError(f'Cannot evaluate `{self!r} < {other!r}`')

    def __gt__(self, other: Any) -> bool:
        """
        >>> 3 < Range(4, 6, 1)
        True
        >>> 4 < Range(4, 6, 1)
        False
        >>> 5 < Range(4, 6, 1)
        False
        >>> 6 < Range(4, 6, 1)
        False
        >>> 7 < Range(4, 6, 1)
        False
        """
        if isinstance(other, int):
            return other < self.lower_bound
        raise TypeError(f'Cannot evaluate `{other!r} < {self!r}`')


def insert_range(ranges: tuple[Range, ...], range_: Range) -> tuple[Range, ...]:
    """
    >>> insert_range((Range(1, 2, 1),), Range(3, 4, 2))
    (Range(lower_bound=1, upper_bound=2, overlaps=1), Range(lower_bound=3, upper_bound=4, overlaps=2))
    >>> insert_range((Range(3, 4, 1),), Range(1, 2, 2))
    (Range(lower_bound=1, upper_bound=2, overlaps=2), Range(lower_bound=3, upper_bound=4, overlaps=1))
    >>> insert_range((Range(1, 2, 1),), Range(1, 2, 2))
    (Range(lower_bound=1, upper_bound=2, overlaps=3),)
    >>> insert_range((Range(1, 2, 1),), Range(2, 3, 2))
    (Range(lower_bound=1, upper_bound=1, overlaps=1), Range(lower_bound=2, upper_bound=2, overlaps=3), Range(lower_bound=3, upper_bound=3, overlaps=2))
    >>> insert_range((Range(1, 3, 1), Range(5, 7, 2), Range(9, 11, 3), Range(13, 15, 4), Range(17, 19, 5)), Range(6, 14, 6))
    (Range(lower_bound=1, upper_bound=3, overlaps=1), Range(lower_bound=5, upper_bound=5, overlaps=2), Range(lower_bound=6, upper_bound=7, overlaps=8), Range(lower_bound=8, upper_bound=8, overlaps=6), Range(lower_bound=9, upper_bound=11, overlaps=9), Range(lower_bound=12, upper_bound=12, overlaps=6), Range(lower_bound=13, upper_bound=14, overlaps=10), Range(lower_bound=15, upper_bound=15, overlaps=4), Range(lower_bound=17, upper_bound=19, overlaps=5))
    >>> insert_range((Range(1, 3, 1), Range(5, 7, 2), Range(9, 11, 3), Range(13, 15, 4), Range(17, 19, 5)), Range(4, 16, 6))
    (Range(lower_bound=1, upper_bound=3, overlaps=1), Range(lower_bound=4, upper_bound=4, overlaps=6), Range(lower_bound=5, upper_bound=7, overlaps=8), Range(lower_bound=8, upper_bound=8, overlaps=6), Range(lower_bound=9, upper_bound=11, overlaps=9), Range(lower_bound=12, upper_bound=12, overlaps=6), Range(lower_bound=13, upper_bound=15, overlaps=10), Range(lower_bound=16, upper_bound=16, overlaps=6), Range(lower_bound=17, upper_bound=19, overlaps=5))
    """
    if len(ranges) == 0:
        return (range_,)

    lower_index = bisect_left(ranges, range_.lower_bound)
    upper_index = bisect_right(ranges, range_.upper_bound)
    new_ranges = list(ranges[:lower_index])
    if lower_index == upper_index:
        new_ranges.append(range_)
    else:
        lower_bound = range_.lower_bound
        upper_bound = range_.upper_bound
        for overlapping_range in ranges[lower_index:upper_index]:
            if overlapping_range.lower_bound < lower_bound:
                new_ranges.append(Range(overlapping_range.lower_bound, lower_bound - 1, overlapping_range.overlaps))
            elif lower_bound < overlapping_range.lower_bound:
                new_ranges.append(Range(lower_bound, overlapping_range.lower_bound - 1, range_.overlaps))
                lower_bound = overlapping_range.lower_bound
            overlap_upper_bound = min(overlapping_range.upper_bound, upper_bound)
            new_ranges.append(Range(lower_bound, overlap_upper_bound, overlapping_range.overlaps + range_.overlaps))
            lower_bound = overlap_upper_bound + 1
        if lower_bound <= overlapping_range.upper_bound:
            new_ranges.append(Range(lower_bound, overlapping_range.upper_bound, overlapping_range.overlaps))
        elif lower_bound <= upper_bound:
            new_ranges.append(Range(lower_bound, upper_bound, range_.overlaps))
    new_ranges.extend(ranges[upper_index:])
    return tuple(new_ranges)


def get_overlaps(ranges: tuple[Range, ...], ingredient: int) -> int:
    index = bisect_left(ranges, ingredient)
    if index < len(ranges) and ranges[index] == ingredient:
        return ranges[index].overlaps
    return 0


########################################################################################################################
# Part 1
########################################################################################################################

def until_blank_line(lines: Iterator[str]) -> Iterator[str]:
    for line in lines:
        if not line:
            break
        yield line


EMPTY_FRESH_INGREDIENT_RANGES: tuple[Range, ...] = ()


def parse_fresh_ingredient_ranges(lines: Iterator[str]) -> tuple[Range, ...]:
    """
    >>> parse_fresh_ingredient_ranges(iter([
    ...     '3-5',
    ...     '10-14',
    ...     '16-20',
    ...     '12-18',
    ... ]))
    (Range(lower_bound=3, upper_bound=5, overlaps=1), Range(lower_bound=10, upper_bound=11, overlaps=1), Range(lower_bound=12, upper_bound=14, overlaps=2), Range(lower_bound=15, upper_bound=15, overlaps=1), Range(lower_bound=16, upper_bound=18, overlaps=2), Range(lower_bound=19, upper_bound=20, overlaps=1))
    """
    unmerged_fresh_ingredient_ranges = (Range.from_line(line) for line in lines)
    return reduce(insert_range, unmerged_fresh_ingredient_ranges, EMPTY_FRESH_INGREDIENT_RANGES)


def parse_available_ingredients(lines: Iterator[str]) -> Iterator[int]:
    return (int(line) for line in lines)


def parse_database(lines: Iterable[str]) -> tuple[tuple[Range, ...], Iterator[int]]:
    lines_iter = iter(lines)
    fresh_ingredient_ranges = parse_fresh_ingredient_ranges(until_blank_line(lines_iter))
    available_ingredients = parse_available_ingredients(lines_iter)
    return (fresh_ingredient_ranges, available_ingredients)


def count_available_fresh_ingredients(lines: Iterable[str]) -> int:
    """
    >>> count_available_fresh_ingredients([
    ...     '3-5',
    ...     '10-14',
    ...     '16-20',
    ...     '12-18',
    ...     '',
    ...     '1',
    ...     '5',
    ...     '8',
    ...     '11',
    ...     '17',
    ...     '32',
    ... ])
    3
    """
    (fresh_ingredient_ranges, available_ingredients) = parse_database(lines)
    return sum(
        bool(get_overlaps(fresh_ingredient_ranges, ingredient))
        for ingredient in available_ingredients
    )


########################################################################################################################
# Part 2
########################################################################################################################

def count_potential_fresh_ingredients(lines: Iterable[str]) -> int:
    """
    >>> count_potential_fresh_ingredients([
    ...     '3-5',
    ...     '10-14',
    ...     '16-20',
    ...     '12-18',
    ...     '',
    ...     '1',
    ...     '5',
    ...     '8',
    ...     '11',
    ...     '17',
    ...     '32',
    ... ])
    14
    """
    (fresh_ingredient_ranges, _) = parse_database(lines)
    return sum(
        range_.upper_bound - range_.lower_bound + 1
        for range_ in fresh_ingredient_ranges
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
        print(count_available_fresh_ingredients(lines))
    elif args.part == 2:
        print(count_potential_fresh_ingredients(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
