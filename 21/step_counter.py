#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable
from enum import Enum
from typing import NamedTuple, Optional


########################################################################################################################
# Map
########################################################################################################################

class Coordinate(NamedTuple):
    x: int
    y: int

    def __str__(self) -> str:
        return f'({self.x}, {self.y})'


class CardinalDirection(Enum):
    NORTH = 'N'
    EAST = 'E'
    SOUTH = 'S'
    WEST = 'W'


def translate(coord: Coordinate, direction: CardinalDirection) -> Coordinate:
    (x, y) = coord
    if direction == CardinalDirection.NORTH:
        return Coordinate(x, y - 1)
    elif direction == CardinalDirection.SOUTH:
        return Coordinate(x, y + 1)
    elif direction == CardinalDirection.EAST:
        return Coordinate(x + 1, y)
    elif direction == CardinalDirection.WEST:
        return Coordinate(x - 1, y)
    else:
        raise ValueError(f'Unexpected direction: {direction!r}')


def wrap(width: int, height: int, coord: Coordinate) -> Coordinate:
    (x, y) = coord
    return Coordinate(x % width, y % height)


class Tile(Enum):
    STARTING_POSITION = 'S'
    GARDEN_PLOT = '.'
    ROCKS = '#'


class Map(NamedTuple):
    width: int
    height: int
    starting_position: Coordinate
    tiles: tuple[tuple[Tile, ...], ...]

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Map':
        width = -1
        starting_position: Optional[Coordinate] = None
        rows: list[tuple[Tile, ...]] = []
        for (y, line) in enumerate(lines):
            # Ensure width is consistent across lines.
            if y == 0:
                width = len(line)
            elif len(line) != width:
                raise ValueError(f'Width of line {y + 1} differs from line 1 ({len(line)} ≠ {width})')
            row: list[Tile] = []
            for (x, char) in enumerate(line):
                tile = Tile(char)
                if tile == Tile.STARTING_POSITION:
                    if starting_position is not None:
                        raise ValueError(f'Starting position specified multiple times: {starting_position} and {Coordinate(x, y)}')
                    starting_position = Coordinate(x, y)
                    tile = Tile.GARDEN_PLOT
                row.append(tile)
            rows.append(tuple(row))
        if starting_position is None:
            raise ValueError(f'Parsed {width} × {y + 1} map, but no starting position was specified')
        return Map(width, y + 1, starting_position, tuple(rows))

    def count_reachable_garden_plots(self, total_steps: int, wraparound: bool) -> int:
        """
        >>> map_ = Map.from_lines([
        ...     '...........',
        ...     '.....###.#.',
        ...     '.###.##..#.',
        ...     '..#.#...#..',
        ...     '....#.#....',
        ...     '.##..S####.',
        ...     '.##..#...#.',
        ...     '.......##..',
        ...     '.##.#.####.',
        ...     '.##..##.##.',
        ...     '...........',
        ... ])
        >>> map_.count_reachable_garden_plots(6, False)
        16
        >>> map_.count_reachable_garden_plots(6, True)
        16
        >>> map_.count_reachable_garden_plots(10, True)
        50
        >>> map_.count_reachable_garden_plots(50, True)
        1594
        >>> map_.count_reachable_garden_plots(100, True)
        6536
        >>> # map_.count_reachable_garden_plots(500, True)
        >>> # 167004
        >>> # map_.count_reachable_garden_plots(1000, True)
        >>> # 668697
        >>> # map_.count_reachable_garden_plots(5000, True)
        >>> # 16733044
        """
        assert total_steps >= 1
        visited_garden_plots: set[Coordinate] = set()
        frontier: list[tuple[int, Coordinate, Coordinate]] = [(total_steps, self.starting_position, self.starting_position)]
        last_steps_remaining = total_steps
        reachable_garden_plots = 0
        while frontier:
            (steps_remaining, wrapped_position, position) = frontier.pop(0)
            if steps_remaining != last_steps_remaining:
                last_steps_remaining = steps_remaining
                # By definition, when we take a next step, we can't be where we were in the previous step.
                reachable_garden_plots = len(visited_garden_plots) - reachable_garden_plots
            assert steps_remaining >= 0
            assert self.tiles[wrapped_position.y][wrapped_position.x] == Tile.GARDEN_PLOT
            if position in visited_garden_plots:
                continue
            visited_garden_plots.add(position)
            if steps_remaining == 0:
                continue
            next_steps_remaining = steps_remaining - 1
            for next_position in (translate(position, direction) for direction in CardinalDirection):
                next_wrapped_position = wrap(self.width, self.height, next_position)
                if not wraparound and (next_wrapped_position != next_position):
                    continue
                if self.tiles[next_wrapped_position.y][next_wrapped_position.x] != Tile.GARDEN_PLOT:
                    continue
                if next_position in visited_garden_plots:
                    continue
                frontier.append((next_steps_remaining, next_wrapped_position, next_position))
        return len(visited_garden_plots) - reachable_garden_plots


########################################################################################################################
# Part 1
########################################################################################################################

def count_reachable_garden_plots(lines: Iterable[str]) -> int:
    map_ = Map.from_lines(lines)
    return map_.count_reachable_garden_plots(64, False)


########################################################################################################################
# Part 2
########################################################################################################################

def count_contrived_reachable_garden_plots(lines: Iterable[str]) -> int:
    map_ = Map.from_lines(lines)
    return map_.count_reachable_garden_plots(26501365, True)


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
        print(count_reachable_garden_plots(lines))
    elif args.part == 2:
        print(count_contrived_reachable_garden_plots(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
