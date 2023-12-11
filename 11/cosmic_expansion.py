#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable
from itertools import combinations
from typing import NamedTuple


########################################################################################################################
# Star map
########################################################################################################################

class Coordinate(NamedTuple):
    x: int
    y: int


EMPTY_SPACE = '.'
GALAXY = '#'


class StarMap(NamedTuple):
    galaxy_coordinates: set[Coordinate]
    expanded_galaxy_coordinates: set[Coordinate]
    empty_columns: set[int]
    empty_rows: set[int]

    @classmethod
    def from_lines(cls, lines: Iterable[str], expansion_factor: int) -> 'StarMap':
        width = -1
        galaxy_coordinates: set[Coordinate] = set()
        empty_columns_mask: list[bool] = []
        empty_rows: set[int] = set()
        for (y, line) in enumerate(lines):
            # Ensure width is consistent across lines.
            if y == 0:
                width = len(line)
                assert not empty_columns_mask
                empty_columns_mask = [True] * width
            elif len(line) != width:
                raise ValueError(f'Width of line {y + 1} differs from line 1 ({len(line)} ≠ {width})')

            is_row_empty = True
            for (x, char) in enumerate(line):
                if char == GALAXY:
                    galaxy_coordinates.add(Coordinate(x, y))
                    empty_columns_mask[x] = False
                    is_row_empty = False
                else:
                    assert char == EMPTY_SPACE
            if is_row_empty:
                empty_rows.add(y)
        empty_columns = set(x for (x, is_empty_column) in enumerate(empty_columns_mask) if is_empty_column)

        expanded_galaxy_coordinates: set[Coordinate] = set()
        for galaxy_coordinate in galaxy_coordinates:
            columns_to_expand = len(list(x for x in empty_columns if x < galaxy_coordinate.x))
            rows_to_expand = len(list(y for y in empty_rows if y < galaxy_coordinate.y))
            x_delta = (columns_to_expand * expansion_factor) - columns_to_expand
            y_delta = (rows_to_expand * expansion_factor) - rows_to_expand
            expanded_galaxy_coordinates.add(Coordinate(galaxy_coordinate.x + x_delta, galaxy_coordinate.y + y_delta))

        return StarMap(galaxy_coordinates, expanded_galaxy_coordinates, empty_columns, empty_rows)


def manhattan_distance(a: Coordinate, b: Coordinate) -> int:
    return abs(a.x - b.x) + abs(a.y - b.y)


def sum_shortest_path_between_galaxy_pairs(lines: Iterable[str], expansion_factor: int) -> int:
    """
    >>> sum_shortest_path_between_galaxy_pairs([
    ...     '...#......',
    ...     '.......#..',
    ...     '#.........',
    ...     '..........',
    ...     '......#...',
    ...     '.#........',
    ...     '.........#',
    ...     '..........',
    ...     '.......#..',
    ...     '#...#.....',
    ... ], 2)
    374
    >>> sum_shortest_path_between_galaxy_pairs([
    ...     '...#......',
    ...     '.......#..',
    ...     '#.........',
    ...     '..........',
    ...     '......#...',
    ...     '.#........',
    ...     '.........#',
    ...     '..........',
    ...     '.......#..',
    ...     '#...#.....',
    ... ], 10)
    1030
    >>> sum_shortest_path_between_galaxy_pairs([
    ...     '...#......',
    ...     '.......#..',
    ...     '#.........',
    ...     '..........',
    ...     '......#...',
    ...     '.#........',
    ...     '.........#',
    ...     '..........',
    ...     '.......#..',
    ...     '#...#.....',
    ... ], 100)
    8410
    """
    star_map = StarMap.from_lines(lines, expansion_factor)
    galaxy_pairs = combinations(star_map.expanded_galaxy_coordinates, 2)
    return sum(map(lambda pair: manhattan_distance(*pair), galaxy_pairs))


########################################################################################################################
# Part 1
########################################################################################################################

def sum_shortest_path_between_galaxy_pairs_with_two_times_expansion(lines: Iterable[str]) -> int:
    return sum_shortest_path_between_galaxy_pairs(lines, 2)


########################################################################################################################
# Part 2
########################################################################################################################

def sum_shortest_path_between_galaxy_pairs_with_million_times_expansion(lines: Iterable[str]) -> int:
    return sum_shortest_path_between_galaxy_pairs(lines, 1_000_000)


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
        print(sum_shortest_path_between_galaxy_pairs_with_two_times_expansion(lines))
    elif args.part == 2:
        print(sum_shortest_path_between_galaxy_pairs_with_million_times_expansion(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
