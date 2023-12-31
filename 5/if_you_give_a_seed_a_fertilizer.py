#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from bisect import bisect_left
from collections.abc import Iterator
from dataclasses import dataclass
import re
from typing import Any, NamedTuple, Optional


########################################################################################################################
# Almanac
########################################################################################################################

@dataclass(frozen=True)
class Range:
    """
    Represent a right-open non-empty integer interval.
    """
    min_inclusive: int
    max_exclusive: int

    def __post_init__(self) -> None:
        """
        >>> Range(1, 2)
        Range(min_inclusive=1, max_exclusive=2)
        >>> Range(1, 1)
        Traceback (most recent call last):
            ...
        ValueError: 1 ≮ 1
        >>> Range(2, 2)
        Traceback (most recent call last):
            ...
        ValueError: 2 ≮ 2
        """
        if self.min_inclusive >= self.max_exclusive:
            raise ValueError(f'{self.min_inclusive} ≮ {self.max_exclusive}')

    def __contains__(self, item: Any) -> bool:
        """
        >>> list(x in Range(2, 4) for x in range(1, 6))
        [False, True, True, False, False]
        >>> 'a' in Range(2, 4)
        Traceback (most recent call last):
            ...
        TypeError: Cannot evaluate `'a' in Range(min_inclusive=2, max_exclusive=4)`
        """
        if isinstance(item, int):
            return self.min_inclusive <= item < self.max_exclusive
        raise TypeError(f'Cannot evaluate `{item!r} in {self!r}`')

    def __lt__(self, other: Any) -> bool:
        """
        >>> Range(1, 3) < Range(4, 6)
        True
        >>> Range(1, 3) < Range(3, 6)
        True
        >>> Range(1, 3) < Range(2, 6)
        False
        >>> Range(2, 6) < Range(1, 3)
        False
        >>> Range(3, 6) < Range(1, 3)
        False
        >>> Range(4, 6) < Range(1, 3)
        False
        """
        if isinstance(other, Range):
            return self.max_exclusive <= other.min_inclusive
        raise TypeError(f'Cannot evaluate `{self!r} < {other!r}`')


NUMBER_DELIMITER = ' '


class Map(NamedTuple):
    transpositions: tuple[tuple[Range, int], ...]

    @classmethod
    def from_lines(cls, lines: Iterator[str]) -> 'Map':
        transpositions: list[tuple[Range, int]] = []
        while True:
            try:
                line = next(lines)
            except StopIteration:
                break
            if not line:
                break
            (destination_range_start, source_range_start, source_range_length) = (int(x) for x in line.split(NUMBER_DELIMITER))
            range_ = Range(source_range_start, source_range_start + source_range_length)
            transposition = (range_, destination_range_start)
            # TODO: verify ranges don't overlap.
            insertion_point = bisect_left(transpositions, transposition)
            transpositions.insert(insertion_point, transposition)
        return Map(tuple(transpositions))

    def transpose(self, source_number: int) -> int:
        # TODO: binary search.
        for (source_range, destination_range_start) in self.transpositions:
            if source_number in source_range:
                return source_number - source_range.min_inclusive + destination_range_start
        return source_number

    def transpose_range(self, range_: Range) -> Iterator[tuple[Range, Range]]:
        """
        >>> map_ = Map.from_lines(iter([
        ...     '100 10 10',
        ...     '200 20 10',
        ...     '300 35 10',
        ... ]))
        >>> list(map_.transpose_range(Range(5, 50)))
        [(Range(min_inclusive=5, max_exclusive=10), Range(min_inclusive=5, max_exclusive=10)), (Range(min_inclusive=10, max_exclusive=20), Range(min_inclusive=100, max_exclusive=110)), (Range(min_inclusive=20, max_exclusive=30), Range(min_inclusive=200, max_exclusive=210)), (Range(min_inclusive=30, max_exclusive=35), Range(min_inclusive=30, max_exclusive=35)), (Range(min_inclusive=35, max_exclusive=45), Range(min_inclusive=300, max_exclusive=310)), (Range(min_inclusive=45, max_exclusive=50), Range(min_inclusive=45, max_exclusive=50))]
        >>> list(map_.transpose_range(Range(5, 9)))
        [(Range(min_inclusive=5, max_exclusive=9), Range(min_inclusive=5, max_exclusive=9))]
        >>> list(map_.transpose_range(Range(5, 10)))
        [(Range(min_inclusive=5, max_exclusive=10), Range(min_inclusive=5, max_exclusive=10))]
        >>> list(map_.transpose_range(Range(5, 11)))
        [(Range(min_inclusive=5, max_exclusive=10), Range(min_inclusive=5, max_exclusive=10)), (Range(min_inclusive=10, max_exclusive=11), Range(min_inclusive=100, max_exclusive=101))]
        >>> list(map_.transpose_range(Range(44, 50)))
        [(Range(min_inclusive=44, max_exclusive=45), Range(min_inclusive=309, max_exclusive=310)), (Range(min_inclusive=45, max_exclusive=50), Range(min_inclusive=45, max_exclusive=50))]
        >>> list(map_.transpose_range(Range(45, 50)))
        [(Range(min_inclusive=45, max_exclusive=50), Range(min_inclusive=45, max_exclusive=50))]
        >>> list(map_.transpose_range(Range(46, 50)))
        [(Range(min_inclusive=46, max_exclusive=50), Range(min_inclusive=46, max_exclusive=50))]
        >>> list(map_.transpose_range(Range(31, 34)))
        [(Range(min_inclusive=31, max_exclusive=34), Range(min_inclusive=31, max_exclusive=34))]
        >>> list(map_.transpose_range(Range(30, 35)))
        [(Range(min_inclusive=30, max_exclusive=35), Range(min_inclusive=30, max_exclusive=35))]
        >>> list(map_.transpose_range(Range(29, 36)))
        [(Range(min_inclusive=29, max_exclusive=30), Range(min_inclusive=209, max_exclusive=210)), (Range(min_inclusive=30, max_exclusive=35), Range(min_inclusive=30, max_exclusive=35)), (Range(min_inclusive=35, max_exclusive=36), Range(min_inclusive=300, max_exclusive=301))]
        """
        # TODO: mapping isn't guaranteed to be bijective. At the very least, we should check that the destination ranges
        # don't overlap.
        range_start = range_.min_inclusive
        range_end = range_.max_exclusive
        for (source_range, destination_range_start) in self.transpositions:
            if range_start < source_range.min_inclusive:
                if range_end <= source_range.min_inclusive:
                    yield (Range(range_start, range_end), Range(range_start, range_end))
                    return
                yield (Range(range_start, source_range.min_inclusive), Range(range_start, source_range.min_inclusive))
                range_start = source_range.min_inclusive
            if range_start in source_range:
                if range_end <= source_range.max_exclusive:
                    yield (Range(range_start, range_end), Range(range_start - source_range.min_inclusive + destination_range_start, range_end - source_range.min_inclusive + destination_range_start))
                    return
                yield (Range(range_start, source_range.max_exclusive), Range(range_start - source_range.min_inclusive + destination_range_start, source_range.max_exclusive - source_range.min_inclusive + destination_range_start))
                range_start = source_range.max_exclusive
        yield (Range(range_start, range_end), Range(range_start, range_end))


MAP_HEADER_PATTERN = re.compile(r'^([a-z]+)-to-([a-z]+) map:$')


class Almanac(NamedTuple):
    """
    >>> almanac = Almanac.from_lines(iter([
    ...     'seed-to-soil map:',
    ...     '50 98 2',
    ...     '52 50 48',
    ...     '',
    ...     'soil-to-fertilizer map:',
    ...     '0 15 37',
    ...     '37 52 2',
    ...     '39 0 15',
    ...     '',
    ...     'fertilizer-to-water map:',
    ...     '49 53 8',
    ...     '0 11 42',
    ...     '42 0 7',
    ...     '57 7 4',
    ...     '',
    ...     'water-to-light map:',
    ...     '88 18 7',
    ...     '18 25 70',
    ...     '',
    ...     'light-to-temperature map:',
    ...     '45 77 23',
    ...     '81 45 19',
    ...     '68 64 13',
    ...     '',
    ...     'temperature-to-humidity map:',
    ...     '0 69 1',
    ...     '1 0 69',
    ...     '',
    ...     'humidity-to-location map:',
    ...     '60 56 37',
    ...     '56 93 4',
    ... ]))
    >>> almanac
    Almanac(maps={'seed': ('soil', Map(transpositions=((Range(min_inclusive=50, max_exclusive=98), 52), (Range(min_inclusive=98, max_exclusive=100), 50)))), 'soil': ('fertilizer', Map(transpositions=((Range(min_inclusive=0, max_exclusive=15), 39), (Range(min_inclusive=15, max_exclusive=52), 0), (Range(min_inclusive=52, max_exclusive=54), 37)))), 'fertilizer': ('water', Map(transpositions=((Range(min_inclusive=0, max_exclusive=7), 42), (Range(min_inclusive=7, max_exclusive=11), 57), (Range(min_inclusive=11, max_exclusive=53), 0), (Range(min_inclusive=53, max_exclusive=61), 49)))), 'water': ('light', Map(transpositions=((Range(min_inclusive=18, max_exclusive=25), 88), (Range(min_inclusive=25, max_exclusive=95), 18)))), 'light': ('temperature', Map(transpositions=((Range(min_inclusive=45, max_exclusive=64), 81), (Range(min_inclusive=64, max_exclusive=77), 68), (Range(min_inclusive=77, max_exclusive=100), 45)))), 'temperature': ('humidity', Map(transpositions=((Range(min_inclusive=0, max_exclusive=69), 1), (Range(min_inclusive=69, max_exclusive=70), 0)))), 'humidity': ('location', Map(transpositions=((Range(min_inclusive=56, max_exclusive=93), 60), (Range(min_inclusive=93, max_exclusive=97), 56))))})
    >>> almanac.hydrate('seed', 79)
    {'seed': 79, 'soil': 81, 'fertilizer': 81, 'water': 81, 'light': 74, 'temperature': 78, 'humidity': 78, 'location': 82}
    >>> almanac.hydrate('seed', 14)
    {'seed': 14, 'soil': 14, 'fertilizer': 53, 'water': 49, 'light': 42, 'temperature': 42, 'humidity': 43, 'location': 43}
    >>> almanac.hydrate('seed', 55)
    {'seed': 55, 'soil': 57, 'fertilizer': 57, 'water': 53, 'light': 46, 'temperature': 82, 'humidity': 82, 'location': 86}
    >>> almanac.hydrate('seed', 13)
    {'seed': 13, 'soil': 13, 'fertilizer': 52, 'water': 41, 'light': 34, 'temperature': 34, 'humidity': 35, 'location': 35}
    """
    maps: dict[str, tuple[str, Map]]

    @classmethod
    def from_lines(cls, lines: Iterator[str]) -> 'Almanac':
        maps: dict[str, tuple[str, Map]] = {}
        prev_destination_category: Optional[str] = None
        while True:
            try:
                line = next(lines)
            except StopIteration:
                break
            match = MAP_HEADER_PATTERN.fullmatch(line)
            if not match:
                raise ValueError(f'Map header line {line!r} does not match '
                                 f'expected pattern /{MAP_HEADER_PATTERN.pattern}/')
            (source_category, destination_category) = match.groups()
            if source_category in maps:
                raise ValueError(f'Encountered duplicate map from source category {source_category!r}')
            if destination_category in maps:
                raise ValueError(f'Encountered unexpected destination category {destination_category!r}')
            if (prev_destination_category is not None) and (source_category != prev_destination_category):
                raise ValueError(f'Expected source category {prev_destination_category!r} but '
                                 f'encountered source category {source_category!r} instead')
            prev_destination_category = destination_category

            map_ = Map.from_lines(lines)
            maps[source_category] = (destination_category, map_)
        return Almanac(maps)

    def hydrate(self, initial_category: str, initial_number: int) -> dict[str, int]:
        category_numbers = {initial_category: initial_number}
        (source_category, source_number) = (initial_category, initial_number)
        while True:
            if source_category not in self.maps:
                break
            (destination_category, map_) = self.maps[source_category]
            if destination_category in category_numbers:
                raise ValueError(f'Encountered duplicate map to destination category {destination_category!r}')
            destination_number = map_.transpose(source_number)
            category_numbers[destination_category] = destination_number
            (source_category, source_number) = (destination_category, destination_number)
        return category_numbers

    def hydrate_range(self, initial_category: str, initial_range: Range) -> Iterator[dict[str, Range]]:
        (destination_category, map_) = self.maps[initial_category]
        if destination_category in self.maps:
            for (source_range, destination_range) in map_.transpose_range(initial_range):
                for partial_hydration in self.hydrate_range(destination_category, destination_range):
                    yield {initial_category: source_range, **partial_hydration}
        else:
            for (source_range, destination_range) in map_.transpose_range(initial_range):
                yield {initial_category: source_range, destination_category: destination_range}


########################################################################################################################
# Part 1
########################################################################################################################

INITIAL_SEEDS_HEADER = 'seeds: '


def parse_initial_seeds(line: str) -> Iterator[int]:
    """
    >>> list(parse_initial_seeds('seeds: 79 14 55 13'))
    [79, 14, 55, 13]
    >>> list(parse_initial_seeds('samen: 69'))
    Traceback (most recent call last):
        ...
    ValueError: Initial seeds line 'samen: 69' does not start with expected header 'seeds: '
    """
    if not line.startswith(INITIAL_SEEDS_HEADER):
        raise ValueError(f'Initial seeds line {line!r} does not start with '
                         f'expected header {INITIAL_SEEDS_HEADER!r}')
    line = line.removeprefix(INITIAL_SEEDS_HEADER)
    return (int(seed) for seed in line.split(NUMBER_DELIMITER))


def find_lowest_location_number(lines: Iterator[str]) -> int:
    """
    >>> find_lowest_location_number(iter([
    ...     'seeds: 79 14 55 13',
    ...     '',
    ...     'seed-to-soil map:',
    ...     '50 98 2',
    ...     '52 50 48',
    ...     '',
    ...     'soil-to-fertilizer map:',
    ...     '0 15 37',
    ...     '37 52 2',
    ...     '39 0 15',
    ...     '',
    ...     'fertilizer-to-water map:',
    ...     '49 53 8',
    ...     '0 11 42',
    ...     '42 0 7',
    ...     '57 7 4',
    ...     '',
    ...     'water-to-light map:',
    ...     '88 18 7',
    ...     '18 25 70',
    ...     '',
    ...     'light-to-temperature map:',
    ...     '45 77 23',
    ...     '81 45 19',
    ...     '68 64 13',
    ...     '',
    ...     'temperature-to-humidity map:',
    ...     '0 69 1',
    ...     '1 0 69',
    ...     '',
    ...     'humidity-to-location map:',
    ...     '60 56 37',
    ...     '56 93 4',
    ... ]))
    35
    """
    initial_seeds = parse_initial_seeds(next(lines))
    if next(lines):
        raise ValueError('Expected blank line')
    almanac = Almanac.from_lines(lines)
    return min(map(lambda seed: almanac.hydrate('seed', seed)['location'], initial_seeds))


########################################################################################################################
# Part 2
########################################################################################################################

def pairs(iterator: Iterator[int]) -> Iterator[tuple[int, int]]:
    """
    >>> list(pairs(iter([])))
    []
    >>> list(pairs(iter([1, 2, 3, 4, 5, 6])))
    [(1, 2), (3, 4), (5, 6)]
    >>> list(pairs(iter([1, 2, 3, 4, 5])))
    Traceback (most recent call last):
        ...
    ValueError: First value 5 is missing its second value
    """
    while True:
        try:
            first = next(iterator)
        except StopIteration:
            return
        try:
            second = next(iterator)
        except StopIteration:
            raise ValueError(f'First value {first} is missing its second value')
        yield (first, second)


def parse_initial_seed_ranges(line: str) -> Iterator[Range]:
    """
    >>> list(parse_initial_seed_ranges('seeds: 79 14 55 13'))
    [Range(min_inclusive=79, max_exclusive=93), Range(min_inclusive=55, max_exclusive=68)]
    >>> list(parse_initial_seed_ranges('samen: 69 420'))
    Traceback (most recent call last):
        ...
    ValueError: Initial seeds line 'samen: 69 420' does not start with expected header 'seeds: '
    >>> list(parse_initial_seed_ranges('seeds: 69'))
    Traceback (most recent call last):
        ...
    ValueError: First value 69 is missing its second value
    """
    if not line.startswith(INITIAL_SEEDS_HEADER):
        raise ValueError(f'Initial seeds line {line!r} does not start with '
                         f'expected header {INITIAL_SEEDS_HEADER!r}')
    line = line.removeprefix(INITIAL_SEEDS_HEADER)
    for (range_start, range_length) in pairs(int(x) for x in line.split(NUMBER_DELIMITER)):
        yield Range(range_start, range_start + range_length)


def find_lowest_location_number_ex(lines: Iterator[str]) -> int:
    """
    >>> find_lowest_location_number_ex(iter([
    ...     'seeds: 79 14 55 13',
    ...     '',
    ...     'seed-to-soil map:',
    ...     '50 98 2',
    ...     '52 50 48',
    ...     '',
    ...     'soil-to-fertilizer map:',
    ...     '0 15 37',
    ...     '37 52 2',
    ...     '39 0 15',
    ...     '',
    ...     'fertilizer-to-water map:',
    ...     '49 53 8',
    ...     '0 11 42',
    ...     '42 0 7',
    ...     '57 7 4',
    ...     '',
    ...     'water-to-light map:',
    ...     '88 18 7',
    ...     '18 25 70',
    ...     '',
    ...     'light-to-temperature map:',
    ...     '45 77 23',
    ...     '81 45 19',
    ...     '68 64 13',
    ...     '',
    ...     'temperature-to-humidity map:',
    ...     '0 69 1',
    ...     '1 0 69',
    ...     '',
    ...     'humidity-to-location map:',
    ...     '60 56 37',
    ...     '56 93 4',
    ... ]))
    46
    """
    initial_seed_ranges = parse_initial_seed_ranges(next(lines))
    if next(lines):
        raise ValueError('Expected blank line')
    almanac = Almanac.from_lines(lines)
    return min(category_ranges['location'].min_inclusive
               for seed_range in initial_seed_ranges
               for category_ranges in almanac.hydrate_range('seed', seed_range))


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
        print(find_lowest_location_number(lines))
    elif args.part == 2:
        print(find_lowest_location_number_ex(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
