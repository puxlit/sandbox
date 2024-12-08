#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable, Iterator
from itertools import combinations
from typing import NamedTuple


########################################################################################################################
# Map
########################################################################################################################

EMPTY_TILE = '.'


class Coordinate(NamedTuple):
    x: int
    y: int

    def within_bounds(self, width: int, height: int) -> bool:
        return (0 <= self.x < width) and (0 <= self.y < height)

    def antinodes(self, other: 'Coordinate', *, width: int, height: int, include_resonant_harmonics: bool) -> Iterator['Coordinate']:
        delta_x = other.x - self.x
        delta_y = other.y - self.y

        if not include_resonant_harmonics:
            location = Coordinate(self.x - delta_x, self.y - delta_y)
            if location.within_bounds(width, height):
                yield location
            location = Coordinate(other.x + delta_x, other.y + delta_y)
            if location.within_bounds(width, height):
                yield location
            return

        location = self
        while location.within_bounds(width, height):
            yield location
            location = Coordinate(location.x - delta_x, location.y - delta_y)
        location = other
        while location.within_bounds(width, height):
            yield location
            location = Coordinate(location.x + delta_x, location.y + delta_y)


class Map(NamedTuple):
    width: int
    height: int
    antennae: dict[str, set[Coordinate]]

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Map':
        width = -1
        antennae: dict[str, set[Coordinate]] = {}
        for (y, line) in enumerate(lines):
            # Ensure width is consistent across lines.
            if y == 0:
                width = len(line)
            elif len(line) != width:
                raise ValueError(f'Width of line {y + 1} differs from line 1 ({len(line)} ≠ {width})')
            for (x, tile) in enumerate(line):
                if tile == EMPTY_TILE:
                    continue
                code_point = ord(tile)
                if not ((48 <= code_point <= 57) or (65 <= code_point <= 90) or (97 <= code_point <= 122)):
                    raise ValueError(f'Encountered unexpected tile {repr(tile)} on line {y + 1} column {x + 1}')
                antennae.setdefault(tile, set()).add(Coordinate(x, y))
        height = y + 1
        return Map(width, height, antennae)

    def count_unique_antinode_locations(self, *, include_resonant_harmonics: bool) -> int:
        antinodes = set()
        for frequency_antennae in self.antennae.values():
            for (a, b) in combinations(frequency_antennae, 2):
                for location in a.antinodes(b, width=self.width, height=self.height, include_resonant_harmonics=include_resonant_harmonics):
                    antinodes.add(location)
        return len(antinodes)


########################################################################################################################
# Part 1
########################################################################################################################

def count_unique_antinode_locations(lines: Iterable[str]) -> int:
    """
    >>> count_unique_antinode_locations([
    ...     '..........',
    ...     '..........',
    ...     '..........',
    ...     '....a.....',
    ...     '..........',
    ...     '.....a....',
    ...     '..........',
    ...     '..........',
    ...     '..........',
    ...     '..........',
    ... ])
    2
    >>> count_unique_antinode_locations([
    ...     '..........',
    ...     '..........',
    ...     '..........',
    ...     '....a.....',
    ...     '........a.',
    ...     '.....a....',
    ...     '..........',
    ...     '..........',
    ...     '..........',
    ...     '..........',
    ... ])
    4
    >>> count_unique_antinode_locations([
    ...     '..........',
    ...     '..........',
    ...     '..........',
    ...     '....a.....',
    ...     '........a.',
    ...     '.....a....',
    ...     '..........',
    ...     '......A...',
    ...     '..........',
    ...     '..........',
    ... ])
    4
    >>> count_unique_antinode_locations([
    ...     '............',
    ...     '........0...',
    ...     '.....0......',
    ...     '.......0....',
    ...     '....0.......',
    ...     '......A.....',
    ...     '............',
    ...     '............',
    ...     '........A...',
    ...     '.........A..',
    ...     '............',
    ...     '............',
    ... ])
    14
    """
    map_ = Map.from_lines(lines)
    return map_.count_unique_antinode_locations(include_resonant_harmonics=False)


########################################################################################################################
# Part 2
########################################################################################################################

def count_unique_antinode_locations_with_resonant_harmonics(lines: Iterable[str]) -> int:
    """
    >>> count_unique_antinode_locations_with_resonant_harmonics([
    ...     'T.........',
    ...     '...T......',
    ...     '.T........',
    ...     '..........',
    ...     '..........',
    ...     '..........',
    ...     '..........',
    ...     '..........',
    ...     '..........',
    ...     '..........',
    ... ])
    9
    >>> count_unique_antinode_locations_with_resonant_harmonics([
    ...     '............',
    ...     '........0...',
    ...     '.....0......',
    ...     '.......0....',
    ...     '....0.......',
    ...     '......A.....',
    ...     '............',
    ...     '............',
    ...     '........A...',
    ...     '.........A..',
    ...     '............',
    ...     '............',
    ... ])
    34
    """
    map_ = Map.from_lines(lines)
    return map_.count_unique_antinode_locations(include_resonant_harmonics=True)


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
        print(count_unique_antinode_locations(lines))
    elif args.part == 2:
        print(count_unique_antinode_locations_with_resonant_harmonics(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
