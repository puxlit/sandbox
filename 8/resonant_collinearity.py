#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable
from itertools import combinations
from typing import NamedTuple


########################################################################################################################
# Map
########################################################################################################################

EMPTY_TILE = '.'


class Coordinate(NamedTuple):
    x: int
    y: int

    def antinodes(self, other: 'Coordinate') -> tuple['Coordinate', 'Coordinate']:
        delta_x = other.x - self.x
        delta_y = other.y - self.y
        return (
            Coordinate(self.x - delta_x, self.y - delta_y),
            Coordinate(other.x + delta_x, other.y + delta_y),
        )


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

    def within_bounds(self, location: Coordinate) -> bool:
        return (0 <= location.x < self.width) and (0 <= location.y < self.height)

    def count_unique_antinode_locations(self) -> int:
        antinodes = set()
        for frequency_antennae in self.antennae.values():
            for (a, b) in combinations(frequency_antennae, 2):
                for antinode_location in a.antinodes(b):
                    if self.within_bounds(antinode_location):
                        antinodes.add(antinode_location)
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
    return map_.count_unique_antinode_locations()


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
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
