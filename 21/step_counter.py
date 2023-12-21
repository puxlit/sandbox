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


def translate(width: int, height: int, coord: Coordinate, direction: CardinalDirection) -> Optional[Coordinate]:
    (x, y) = coord
    assert 0 <= x < width
    assert 0 <= y < height
    if direction == CardinalDirection.NORTH:
        if y > 0:
            return Coordinate(x, y - 1)
    elif direction == CardinalDirection.SOUTH:
        if y < height - 1:
            return Coordinate(x, y + 1)
    elif direction == CardinalDirection.EAST:
        if x < width - 1:
            return Coordinate(x + 1, y)
    elif direction == CardinalDirection.WEST:
        if x > 0:
            return Coordinate(x - 1, y)
    else:
        raise ValueError(f'Unexpected direction: {direction!r}')
    return None


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

    def count_reachable_garden_plots(self, total_steps: int) -> int:
        """
        >>> Map.from_lines([
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
        ... ]).count_reachable_garden_plots(6)
        16
        """
        assert total_steps >= 1
        visited_garden_plots: set[Coordinate] = set()
        frontier: list[tuple[int, Coordinate]] = [(total_steps, self.starting_position)]
        last_steps_remaining = total_steps
        reachable_garden_plots = 0
        while frontier:
            (steps_remaining, position) = frontier.pop(0)
            if steps_remaining != last_steps_remaining:
                last_steps_remaining = steps_remaining
                reachable_garden_plots = len(visited_garden_plots) - reachable_garden_plots
            assert steps_remaining >= 0
            assert self.tiles[position.y][position.x] == Tile.GARDEN_PLOT
            if position in visited_garden_plots:
                continue
            visited_garden_plots.add(position)
            if steps_remaining == 0:
                continue
            next_steps_remaining = steps_remaining - 1
            for next_position in (translate(self.width, self.height, position, direction) for direction in CardinalDirection):
                if next_position is None:
                    continue
                if self.tiles[next_position.y][next_position.x] != Tile.GARDEN_PLOT:
                    continue
                if next_position in visited_garden_plots:
                    continue
                frontier.append((next_steps_remaining, next_position))
        return len(visited_garden_plots) - reachable_garden_plots


########################################################################################################################
# Part 1
########################################################################################################################

def count_reachable_garden_plots(lines: Iterable[str]) -> int:
    map_ = Map.from_lines(lines)
    return map_.count_reachable_garden_plots(64)


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
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
