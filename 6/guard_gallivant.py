#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable, Iterator
from itertools import cycle
from typing import NamedTuple, Optional


########################################################################################################################
# Map
########################################################################################################################

EMPTY_TILE = '.'
GUARD_TILE = '^'
OBSTRUCTION_TILE = '#'


PATROL_DIRECTIONS = (
    (0, -1),  # Take a step north.
    (1, 0),   # Take a step east.
    (0, 1),   # Take a step south.
    (-1, 0),  # Take a step west.
)


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

    def guard_visited_positions(self) -> Iterator[Coordinate]:
        patrol_direction = cycle(PATROL_DIRECTIONS)
        (step_x, step_y) = next(patrol_direction)
        (curr_x, curr_y) = self.starting_guard_position
        yield self.starting_guard_position
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
                yield Coordinate(curr_x, curr_y)

    def count_cycle_inducing_obstruction_positions(self) -> int:
        obstruction_positions = 0
        evaluated_candidate_positions: set[Coordinate] = set()
        for candidate_position in self.guard_visited_positions():
            if candidate_position in evaluated_candidate_positions:
                # We've already tried spawning an obstruction here.
                continue
            evaluated_candidate_positions.add(candidate_position)
            if candidate_position == self.starting_guard_position:
                # The guard's going to notice if we spawn an obstruction on top of them.
                continue
            (candidate_x, candidate_y) = candidate_position

            patrol_direction = cycle(enumerate(PATROL_DIRECTIONS))
            (direction, (step_x, step_y)) = next(patrol_direction)
            (curr_x, curr_y) = self.starting_guard_position
            guard_visited_positions = {(curr_x, curr_y, direction)}
            while True:
                (next_x, next_y) = (curr_x + step_x, curr_y + step_y)
                if not ((0 <= next_x < self.width) and (0 <= next_y < self.height)):
                    # The guard's left the mapped area.
                    break
                if self.rows[next_y][next_x] or ((next_x == candidate_x) and (next_y == candidate_y)):
                    # Next step is an obstruction. Turn right.
                    (direction, (step_x, step_y)) = next(patrol_direction)
                else:
                    # Next step is empty. Move forward.
                    (curr_x, curr_y) = (next_x, next_y)
                    if (curr_x, curr_y, direction) in guard_visited_positions:
                        # We've entered a cycle!
                        obstruction_positions += 1
                        break
                    guard_visited_positions.add((curr_x, curr_y, direction))
        return obstruction_positions


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
    distinct_guard_visited_positions = set(map_.guard_visited_positions())
    return len(distinct_guard_visited_positions)


########################################################################################################################
# Part 2
########################################################################################################################

def count_cycle_inducing_obstruction_positions(lines: Iterable[str]) -> int:
    """
    >>> count_cycle_inducing_obstruction_positions([
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
    6
    """
    map_ = Map.from_lines(lines)
    return map_.count_cycle_inducing_obstruction_positions()


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
    elif args.part == 2:
        print(count_cycle_inducing_obstruction_positions(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
