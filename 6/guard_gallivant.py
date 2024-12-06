#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable
from itertools import cycle
from typing import NamedTuple, Optional


########################################################################################################################
# Map
########################################################################################################################

EMPTY_TILE = '.'
GUARD_TILE = '^'
OBSTRUCTION_TILE = '#'


class Coordinate(NamedTuple):
    x: int
    y: int


class Map(NamedTuple):
    width: int
    height: int
    rows: tuple[tuple[bool, ...], ...]
    starting_guard_position: Coordinate

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Map':
        width = -1
        rows: list[tuple[bool, ...]] = []
        starting_guard_position: Optional[Coordinate] = None
        for (y, line) in enumerate(lines):
            # Ensure width is consistent across lines.
            if y == 0:
                width = len(line)
            elif len(line) != width:
                raise ValueError(f'Width of line {y + 1} differs from line 1 ({len(line)} ≠ {width})')
            row = []
            for (x, tile) in enumerate(line):
                if tile == EMPTY_TILE:
                    row.append(False)
                elif tile == OBSTRUCTION_TILE:
                    row.append(True)
                elif tile == GUARD_TILE:
                    if starting_guard_position is not None:
                        raise ValueError(f'Encountered a second starting guard tile at {Coordinate(x, y)}; first starting guard tile was at {starting_guard_position}')
                    starting_guard_position = Coordinate(x, y)
                    row.append(False)
                else:
                    raise ValueError(f'Unexpected tile {repr(tile)} at {Coordinate(x, y)}')
            rows.append(tuple(row))
        height = y + 1
        if starting_guard_position is None:
            raise ValueError('Map is missing a starting guard tile')

        return Map(width, height, tuple(rows), starting_guard_position)

    def count_distinct_guard_visited_positions(self) -> int:
        distinct_visited_positions = {self.starting_guard_position}
        patrol_direction = cycle((
            (0, -1),  # Take a step north.
            (1, 0),   # Take a step east.
            (0, 1),   # Take a step south.
            (-1, 0),  # Take a step west.
        ))
        (curr_x, curr_y) = self.starting_guard_position
        (step_x, step_y) = next(patrol_direction)
        while True:
            (next_x, next_y) = (curr_x + step_x, curr_y + step_y)
            if not ((0 <= next_x < self.width) and (0 <= next_y < self.height)):
                # The guard's left the mapped area.
                break
            if self.rows[next_y][next_x]:
                # Next step is an obstruction. Turn right.
                (step_x, step_y) = next(patrol_direction)
            else:
                # Next step is empty. Move forward.
                (curr_x, curr_y) = (next_x, next_y)
                distinct_visited_positions.add(Coordinate(curr_x, curr_y))
        return len(distinct_visited_positions)


########################################################################################################################
# Part 1
########################################################################################################################

def count_distinct_guard_visited_positions(lines: Iterable[str]) -> int:
    """
    >>> count_distinct_guard_visited_positions([
    ...     '....#.....',
    ...     '.........#',
    ...     '..........',
    ...     '..#.......',
    ...     '.......#..',
    ...     '..........',
    ...     '.#..^.....',
    ...     '........#.',
    ...     '#.........',
    ...     '......#...',
    ... ])
    41
    """
    map_ = Map.from_lines(lines)
    return map_.count_distinct_guard_visited_positions()


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
        print(count_distinct_guard_visited_positions(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
