#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable, Iterator
from enum import Enum
from itertools import tee
from typing import NamedTuple


########################################################################################################################
# Platform
########################################################################################################################

class CardinalDirection(Enum):
    NORTH = 'N'
    EAST = 'E'
    SOUTH = 'S'
    WEST = 'W'

    @property
    def reverse(self):
        if self == CardinalDirection.NORTH:
            return CardinalDirection.SOUTH
        elif self == CardinalDirection.SOUTH:
            return CardinalDirection.NORTH
        elif self == CardinalDirection.EAST:
            return CardinalDirection.WEST
        elif self == CardinalDirection.WEST:
            return CardinalDirection.EAST
        else:
            raise ValueError(f'Unexpected direction: {self!r}')


def coordinates(width: int, height: int, main_axis_direction: CardinalDirection) -> Iterator[Iterator[tuple[int, int]]]:
    if main_axis_direction == CardinalDirection.NORTH:
        return (((x, y) for y in range(height - 1, -1, -1)) for x in range(width))
    elif main_axis_direction == CardinalDirection.SOUTH:
        return (((x, y) for y in range(height)) for x in range(width))
    elif main_axis_direction == CardinalDirection.EAST:
        return (((x, y) for x in range(width)) for y in range(height))
    elif main_axis_direction == CardinalDirection.WEST:
        return (((x, y) for x in range(width - 1, -1, -1)) for y in range(height))
    else:
        raise ValueError(f'Unexpected direction: {main_axis_direction!r}')


class Tile(Enum):
    EMPTY_SPACE = '.'
    CUBE_SHAPED_ROCK = '#'
    ROUNDED_ROCK = 'O'


class Platform(NamedTuple):
    width: int
    height: int
    rows: tuple[tuple[Tile, ...], ...] = ()

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Platform':
        width = -1
        rows: list[tuple[Tile, ...]] = []
        for (y, line) in enumerate(lines):
            # Ensure width is consistent across lines.
            if y == 0:
                width = len(line)
            elif len(line) != width:
                raise ValueError(f'Width of line {y + 1} differs from line 1 ({len(line)} ≠ {width})')
            rows.append(tuple(Tile(char) for char in line))
        return Platform(width, y + 1, tuple(rows))

    def __str__(self) -> str:
        return '\n'.join(''.join(tile.value for tile in row) for row in self.rows)

    def tilt(self, direction: CardinalDirection) -> 'Platform':
        r"""
        >>> str(Platform.from_lines([
        ...     'O....#....',
        ...     'O.OO#....#',
        ...     '.....##...',
        ...     'OO.#O....O',
        ...     '.O.....O#.',
        ...     'O.#..O.#.#',
        ...     '..O..#O..O',
        ...     '.......O..',
        ...     '#....###..',
        ...     '#OO..#....',
        ... ]).tilt(CardinalDirection.NORTH))
        'OOOO.#.O..\nOO..#....#\nOO..O##..O\nO..#.OO...\n........#.\n..#....#.#\n..O..#.O.O\n..O.......\n#....###..\n#....#....'
        """
        mutable_rows = list(list(row) for row in self.rows)

        for cross_axis in coordinates(self.width, self.height, direction.reverse):
            (read_pass, write_pass) = tee(cross_axis)
            tilted_main_axis: list[Tile] = []
            for (x, y) in read_pass:
                tile = self.rows[y][x]
                if tile == Tile.ROUNDED_ROCK:
                    try:
                        # We're inserting at the start of the list because there's no `rindex`.
                        insertion_point = tilted_main_axis.index(Tile.CUBE_SHAPED_ROCK)
                    except ValueError:
                        insertion_point = len(tilted_main_axis)
                elif tile in {Tile.EMPTY_SPACE, Tile.CUBE_SHAPED_ROCK}:
                    insertion_point = 0
                else:
                    raise ValueError(f'Unexpected tile: {tile!r}')
                tilted_main_axis.insert(insertion_point, tile)
            tilted_main_axis.reverse()
            for ((x, y), tile) in zip(write_pass, tilted_main_axis):
                mutable_rows[y][x] = tile

        updated_rows = tuple(tuple(row) for row in mutable_rows)
        if updated_rows != self.rows:
            return Platform(self.width, self.height, updated_rows)
        return self

    def run_spin_cycle(self) -> 'Platform':
        r"""
        >>> platform = Platform.from_lines([
        ...     'O....#....',
        ...     'O.OO#....#',
        ...     '.....##...',
        ...     'OO.#O....O',
        ...     '.O.....O#.',
        ...     'O.#..O.#.#',
        ...     '..O..#O..O',
        ...     '.......O..',
        ...     '#....###..',
        ...     '#OO..#....',
        ... ])
        >>> platform_after_one_cycle = platform.run_spin_cycle()
        >>> str(platform_after_one_cycle)
        '.....#....\n....#...O#\n...OO##...\n.OO#......\n.....OOO#.\n.O#...O#.#\n....O#....\n......OOOO\n#...O###..\n#..OO#....'
        >>> platform_after_two_cycles = platform_after_one_cycle.run_spin_cycle()
        >>> str(platform_after_two_cycles)
        '.....#....\n....#...O#\n.....##...\n..O#......\n.....OOO#.\n.O#...O#.#\n....O#...O\n.......OOO\n#..OO###..\n#.OOO#...O'
        >>> platform_after_three_cycles = platform_after_two_cycles.run_spin_cycle()
        >>> str(platform_after_three_cycles)
        '.....#....\n....#...O#\n.....##...\n..O#......\n.....OOO#.\n.O#...O#.#\n....O#...O\n.......OOO\n#...O###.O\n#.OOO#...O'
        """
        return self.tilt(CardinalDirection.NORTH) \
                   .tilt(CardinalDirection.WEST)  \
                   .tilt(CardinalDirection.SOUTH) \
                   .tilt(CardinalDirection.EAST)

    def calculate_support_beam_load(self, direction: CardinalDirection) -> int:
        """
        >>> Platform.from_lines([
        ...     'OOOO.#.O..',
        ...     'OO..#....#',
        ...     'OO..O##..O',
        ...     'O..#.OO...',
        ...     '........#.',
        ...     '..#....#.#',
        ...     '..O..#.O.O',
        ...     '..O.......',
        ...     '#....###..',
        ...     '#....#....',
        ... ]).calculate_support_beam_load(CardinalDirection.NORTH)
        136
        """
        if direction == CardinalDirection.NORTH:
            tile_weights = ((tile, i + 1) for (i, row) in enumerate(reversed(self.rows)) for tile in row)
        elif direction == CardinalDirection.SOUTH:
            tile_weights = ((tile, i + 1) for (i, row) in enumerate(self.rows) for tile in row)
        elif direction == CardinalDirection.EAST:
            tile_weights = ((tile, i + 1) for row in self.rows for (i, tile) in enumerate(row))
        elif direction == CardinalDirection.WEST:
            tile_weights = ((tile, i + 1) for row in self.rows for (i, tile) in enumerate(reversed(row)))
        else:
            raise ValueError(f'Unexpected direction: {direction!r}')
        return sum(weight for (tile, weight) in tile_weights if (tile == Tile.ROUNDED_ROCK))


########################################################################################################################
# Part 1
########################################################################################################################

def tilt_north_and_calculate_support_beam_load(lines: Iterable[str]) -> int:
    """
    >>> tilt_north_and_calculate_support_beam_load([
    ...     'O....#....',
    ...     'O.OO#....#',
    ...     '.....##...',
    ...     'OO.#O....O',
    ...     '.O.....O#.',
    ...     'O.#..O.#.#',
    ...     '..O..#O..O',
    ...     '.......O..',
    ...     '#....###..',
    ...     '#OO..#....',
    ... ])
    136
    """
    platform = Platform.from_lines(lines)
    platform = platform.tilt(CardinalDirection.NORTH)
    return platform.calculate_support_beam_load(CardinalDirection.NORTH)


########################################################################################################################
# Part 2
########################################################################################################################

ONE_BILLION = 1_000_000_000


def run_billion_spin_cycles_and_calculate_support_beam_load(lines: Iterable[str]) -> int:
    """
    >>> run_billion_spin_cycles_and_calculate_support_beam_load([
    ...     'O....#....',
    ...     'O.OO#....#',
    ...     '.....##...',
    ...     'OO.#O....O',
    ...     '.O.....O#.',
    ...     'O.#..O.#.#',
    ...     '..O..#O..O',
    ...     '.......O..',
    ...     '#....###..',
    ...     '#OO..#....',
    ... ])
    64
    """
    platform = Platform.from_lines(lines)
    witnessed_platforms = {platform: 0}
    witnessed_platforms_sequence = [platform]
    for i in range(1, ONE_BILLION + 1):
        platform = platform.run_spin_cycle()
        if platform in witnessed_platforms:
            break
        witnessed_platforms[platform] = i
        witnessed_platforms_sequence.append(platform)
    cycle_start = witnessed_platforms[platform]
    cycle_length = i - cycle_start
    if cycle_length > 0:
        cycle_pos = cycle_start + ((ONE_BILLION - i) % cycle_length)
        platform = witnessed_platforms_sequence[cycle_pos]
    return platform.calculate_support_beam_load(CardinalDirection.NORTH)


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
        print(tilt_north_and_calculate_support_beam_load(lines))
    elif args.part == 2:
        print(run_billion_spin_cycles_and_calculate_support_beam_load(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
