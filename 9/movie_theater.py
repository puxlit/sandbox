#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable, Iterator
from heapq import heappop, heappush
from itertools import combinations
from typing import NamedTuple


########################################################################################################################
# Part 1
########################################################################################################################

COORDINATE_DELIMITER = ','


class RedTile(NamedTuple):
    x: int
    y: int

    @classmethod
    def from_line(cls, line: str) -> 'RedTile':
        (raw_x, raw_y) = line.split(COORDINATE_DELIMITER)
        return RedTile(int(raw_x), int(raw_y))


def calculate_area(a: RedTile, b: RedTile) -> int:
    return (abs(a.x - b.x) + 1) * (abs(a.y - b.y) + 1)


def pairs_by_largest_area(red_tiles: Iterable[RedTile]) -> Iterator[tuple[int, RedTile, RedTile]]:
    # A complete graph of n vertices has n(n-1)÷2 edges. So 496 vertices would have 122,760 edges.
    pairs: list[tuple[int, RedTile, RedTile]] = []
    for (a, b) in combinations(red_tiles, 2):
        area = calculate_area(a, b)
        # If we were on Python 3.14, we could use `heappush_max`.
        heappush(pairs, (-area, a, b))
    while pairs:
        # If we were on Python 3.14, we could use `heappop_max`.
        (negative_area, a, b) = heappop(pairs)
        yield (-negative_area, a, b)


def parse_red_tiles(lines: Iterable[str]) -> Iterator[RedTile]:
    for line in lines:
        yield RedTile.from_line(line)


########################################################################################################################
# Part 1
########################################################################################################################

def calculate_largest_area(lines: Iterable[str]) -> int:
    """
    >>> calculate_largest_area([
    ...     '7,1',
    ...     '11,1',
    ...     '11,7',
    ...     '9,7',
    ...     '9,5',
    ...     '2,5',
    ...     '2,3',
    ...     '7,3',
    ... ])
    50
    """
    red_tiles = parse_red_tiles(lines)
    (area, _, _) = next(pairs_by_largest_area(red_tiles))
    return area


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
        print(calculate_largest_area(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
