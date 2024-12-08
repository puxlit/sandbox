#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable
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
    antinodes: dict[str, set[Coordinate]]

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Map':
        width = -1
        antennae: dict[str, set[Coordinate]] = {}
        antinodes: dict[str, set[Coordinate]] = {}
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
                antenna_location = Coordinate(x, y)
                frequency_antennae = antennae.setdefault(tile, set())
                frequency_antinodes = antinodes.setdefault(tile, set())
                for other_antenna_location in frequency_antennae:
                    frequency_antinodes.update(antenna_location.antinodes(other_antenna_location))
                frequency_antennae.add(antenna_location)
        height = y + 1
        return Map(width, height, antennae, antinodes)

    def within_bounds(self, location: Coordinate) -> bool:
        return (0 <= location.x < self.width) and (0 <= location.y < self.height)


########################################################################################################################
# Part 1
########################################################################################################################

def count_unique_antinode_locations_within_bounds(lines: Iterable[str]) -> int:
    """
    >>> count_unique_antinode_locations_within_bounds([
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
    >>> count_unique_antinode_locations_within_bounds([
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
    >>> count_unique_antinode_locations_within_bounds([
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
    >>> count_unique_antinode_locations_within_bounds([
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
    unique_antinode_locations_within_bounds = set(
        antinode_location
        for frequency_antinodes in map_.antinodes.values()
        for antinode_location in frequency_antinodes
        if map_.within_bounds(antinode_location)
    )
    return len(unique_antinode_locations_within_bounds)


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
        print(count_unique_antinode_locations_within_bounds(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
