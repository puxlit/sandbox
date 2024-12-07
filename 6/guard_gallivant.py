#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from bisect import bisect_left
from collections.abc import Iterable, Iterator
from enum import Enum
from typing import NamedTuple, Optional

from typing_extensions import assert_never


########################################################################################################################
# Map
########################################################################################################################

EMPTY_TILE = '.'
GUARD_TILE = '^'
OBSTRUCTION_TILE = '#'


class PatrolDirection(Enum):
    NORTH = (0, -1)
    EAST = (1, 0)
    SOUTH = (0, 1)
    WEST = (-1, 0)

    @property
    def next(self) -> 'PatrolDirection':
        if self == PatrolDirection.NORTH:
            return PatrolDirection.EAST
        elif self == PatrolDirection.EAST:
            return PatrolDirection.SOUTH
        elif self == PatrolDirection.SOUTH:
            return PatrolDirection.WEST
        elif self == PatrolDirection.WEST:
            return PatrolDirection.NORTH
        assert_never(self)


class Coordinate(NamedTuple):
    x: int
    y: int


class Leg(NamedTuple):
    start: Coordinate
    direction: PatrolDirection
    distance: int

    def steps(self) -> Iterable[Coordinate]:
        (curr_x, curr_y) = self.start
        (step_x, step_y) = self.direction.value
        yield self.start
        for _ in range(self.distance):
            curr_x += step_x
            curr_y += step_y
            yield Coordinate(curr_x, curr_y)


class Map(NamedTuple):
    width: int
    height: int
    tiles: tuple[tuple[bool, ...], ...]
    rows: tuple[tuple[int, ...], ...]
    columns: tuple[tuple[int, ...], ...]
    starting_guard_position: Coordinate

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Map':
        width = -1
        tiles: list[tuple[bool, ...]] = []  # Build a bitmap of obstructions.
        rows: list[tuple[int, ...]] = []    # Build a sorted tuple of obstruction abscissas for each row.
        columns: list[list[int]] = []       # Build a sorted tuple of obstruction ordinates for each column.
        starting_guard_position: Optional[Coordinate] = None
        for (y, line) in enumerate(lines):
            # Ensure width is consistent across lines.
            if y == 0:
                width = len(line)
                columns.extend([] for _ in range(width))
            elif len(line) != width:
                raise ValueError(f'Width of line {y + 1} differs from line 1 ({len(line)} ≠ {width})')
            tiles_row = []
            row = []
            for (x, tile) in enumerate(line):
                if tile == EMPTY_TILE:
                    tiles_row.append(False)
                elif tile == OBSTRUCTION_TILE:
                    tiles_row.append(True)
                    row.append(x)
                    columns[x].append(y)
                elif tile == GUARD_TILE:
                    tiles_row.append(False)
                    if starting_guard_position is not None:
                        raise ValueError(f'Encountered a second starting guard tile at {Coordinate(x, y)}; first starting guard tile was at {starting_guard_position}')
                    starting_guard_position = Coordinate(x, y)
                else:
                    raise ValueError(f'Unexpected tile {repr(tile)} at {Coordinate(x, y)}')
            tiles.append(tuple(tiles_row))
            rows.append(tuple(row))
        height = y + 1
        if starting_guard_position is None:
            raise ValueError('Map is missing a starting guard tile')

        return Map(
            width, height,
            tuple(tiles), tuple(rows), tuple(tuple(column) for column in columns),
            starting_guard_position,
        )

    def stride(self, start: Coordinate, direction: PatrolDirection, *, extra_obstruction: Optional[Coordinate] = None) -> tuple[Leg, Optional[Coordinate]]:
        """
        >>> map_ = Map.from_lines([
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
        >>> map_.stride(Coordinate(4, 6), PatrolDirection.NORTH)
        (Leg(start=Coordinate(x=4, y=6), direction=<PatrolDirection.NORTH: (0, -1)>, distance=5), Coordinate(x=4, y=1))
        >>> map_.stride(Coordinate(5, 6), PatrolDirection.NORTH)
        (Leg(start=Coordinate(x=5, y=6), direction=<PatrolDirection.NORTH: (0, -1)>, distance=6), None)
        >>> map_.stride(Coordinate(8, 1), PatrolDirection.EAST)
        (Leg(start=Coordinate(x=8, y=1), direction=<PatrolDirection.EAST: (1, 0)>, distance=0), Coordinate(x=8, y=1))
        >>> map_.stride(Coordinate(9, 2), PatrolDirection.EAST)
        (Leg(start=Coordinate(x=9, y=2), direction=<PatrolDirection.EAST: (1, 0)>, distance=0), None)
        >>> map_.stride(Coordinate(8, 5), PatrolDirection.SOUTH)
        (Leg(start=Coordinate(x=8, y=5), direction=<PatrolDirection.SOUTH: (0, 1)>, distance=1), Coordinate(x=8, y=6))
        >>> map_.stride(Coordinate(7, 5), PatrolDirection.SOUTH)
        (Leg(start=Coordinate(x=7, y=5), direction=<PatrolDirection.SOUTH: (0, 1)>, distance=4), None)
        >>> map_.stride(Coordinate(9, 7), PatrolDirection.WEST)
        (Leg(start=Coordinate(x=9, y=7), direction=<PatrolDirection.WEST: (-1, 0)>, distance=0), Coordinate(x=9, y=7))
        >>> map_.stride(Coordinate(0, 6), PatrolDirection.WEST)
        (Leg(start=Coordinate(x=0, y=6), direction=<PatrolDirection.WEST: (-1, 0)>, distance=0), None)
        """
        (start_x, start_y) = start
        # Ensure we're within bounds.
        assert ((0 <= start_x < self.width) and (0 <= start_y < self.height))
        # Ensure we're not starting on an obstruction.
        assert (not self.tiles[start_y][start_x]) and ((extra_obstruction is None) or not ((start_x == extra_obstruction.x) and (start_y == extra_obstruction.y)))
        if (direction == PatrolDirection.NORTH) or (direction == PatrolDirection.SOUTH):
            column = self.columns[start_x]
            if (extra_obstruction is not None) and (extra_obstruction.x == start_x):
                assert extra_obstruction.y not in column
                i = bisect_left(column, extra_obstruction.y)
                column = column[:i] + (extra_obstruction.y,) + column[i:]
            i = bisect_left(column, start_y)
            if direction == PatrolDirection.NORTH:
                obstruction_hit = i > 0
                end_y = (column[i - 1] + 1) if obstruction_hit else 0
            elif direction == PatrolDirection.SOUTH:
                obstruction_hit = i < len(column)
                end_y = (column[i] - 1) if obstruction_hit else (self.height - 1)
            else:
                assert_never(direction)
            distance = abs(end_y - start_y)
            end_x = start_x
        elif (direction == PatrolDirection.EAST) or (direction == PatrolDirection.WEST):
            row = self.rows[start_y]
            if (extra_obstruction is not None) and (extra_obstruction.y == start_y):
                assert extra_obstruction.x not in row
                i = bisect_left(row, extra_obstruction.x)
                row = row[:i] + (extra_obstruction.x,) + row[i:]
            i = bisect_left(row, start_x)
            if direction == PatrolDirection.WEST:
                obstruction_hit = i > 0
                end_x = (row[i - 1] + 1) if obstruction_hit else 0
            elif direction == PatrolDirection.EAST:
                obstruction_hit = i < len(row)
                end_x = (row[i] - 1) if obstruction_hit else (self.width - 1)
            else:
                assert_never(direction)
            distance = abs(end_x - start_x)
            end_y = start_y
        else:
            assert_never(direction)
        leg = Leg(start, direction, distance)
        return (leg, Coordinate(end_x, end_y) if obstruction_hit else None)

    def guard_legs(self, *, start: Optional[Coordinate] = None, direction: Optional[PatrolDirection] = None, extra_obstruction: Optional[Coordinate] = None) -> Iterator[Leg]:
        """
        >>> tuple(Map.from_lines([
        ...     '.#........',
        ...     '.^......#.',
        ... ]).guard_legs())
        (Leg(start=Coordinate(x=1, y=1), direction=<PatrolDirection.NORTH: (0, -1)>, distance=0), Leg(start=Coordinate(x=2, y=1), direction=<PatrolDirection.EAST: (1, 0)>, distance=5))
        >>> tuple(Map.from_lines([
        ...     '.#........',
        ...     '.^......#.',
        ...     '..........',
        ... ]).guard_legs())
        (Leg(start=Coordinate(x=1, y=1), direction=<PatrolDirection.NORTH: (0, -1)>, distance=0), Leg(start=Coordinate(x=2, y=1), direction=<PatrolDirection.EAST: (1, 0)>, distance=5), Leg(start=Coordinate(x=7, y=2), direction=<PatrolDirection.SOUTH: (0, 1)>, distance=0))
        >>> tuple(Map.from_lines([
        ...     '.#........',
        ...     '.^......#.',
        ...     '.......#..',
        ... ]).guard_legs())
        (Leg(start=Coordinate(x=1, y=1), direction=<PatrolDirection.NORTH: (0, -1)>, distance=0), Leg(start=Coordinate(x=2, y=1), direction=<PatrolDirection.EAST: (1, 0)>, distance=5), Leg(start=Coordinate(x=6, y=1), direction=<PatrolDirection.WEST: (-1, 0)>, distance=6))
        """
        if start is None:
            start = self.starting_guard_position
        if direction is None:
            direction = PatrolDirection.NORTH
        if extra_obstruction is not None:
            assert extra_obstruction != start
            assert not self.tiles[extra_obstruction.y][extra_obstruction.x]
        while True:
            (leg, end) = self.stride(start, direction, extra_obstruction=extra_obstruction)
            yield leg
            if end is None:
                # The guard's left the mapped area.
                break
            next_direction = direction.next
            while True:
                (step_x, step_y) = next_direction.value
                start = Coordinate(end.x + step_x, end.y + step_y)
                if not ((0 <= start.x < self.width) and (0 <= start.y < self.height)):
                    # The guard's left the mapped area.
                    return
                if (not self.tiles[start.y][start.x]) and ((extra_obstruction is None) or not ((start.x == extra_obstruction.x) and (start.y == extra_obstruction.y))):
                    # A step in this direction is obstruction-free.
                    direction = next_direction
                    break
                next_direction = next_direction.next
                if next_direction == direction:
                    # We're somehow trapped! Obstructions are all around us!
                    assert False

    def count_cycle_inducing_obstruction_positions(self) -> int:
        obstruction_positions = 0
        old_guard_legs = list(self.guard_legs())
        evaluated_candidate_positions: set[Coordinate] = set()
        for (i, old_guard_leg) in enumerate(old_guard_legs):
            for candidate_position in old_guard_leg.steps():
                if candidate_position in evaluated_candidate_positions:
                    # We've already tried spawning an obstruction here.
                    continue
                evaluated_candidate_positions.add(candidate_position)
                if candidate_position == self.starting_guard_position:
                    # The guard's going to notice if we spawn an obstruction on top of them.
                    continue

                if candidate_position != old_guard_leg.start:
                    start = old_guard_leg.start
                    direction = old_guard_leg.direction
                    new_guard_legs = set(old_guard_legs[:i])
                else:
                    start = old_guard_legs[i - 1].start
                    direction = old_guard_legs[i - 1].direction
                    new_guard_legs = set(old_guard_legs[:i - 1])
                for new_guard_leg in self.guard_legs(start=start, direction=direction, extra_obstruction=candidate_position):
                    if new_guard_leg in new_guard_legs:
                        # We've entered a cycle!
                        obstruction_positions += 1
                        break
                    new_guard_legs.add(new_guard_leg)
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
    distinct_guard_visited_positions = set(
        coordinate
        for leg in map_.guard_legs()
        for coordinate in leg.steps()
    )
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
