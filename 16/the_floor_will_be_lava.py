#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable
from enum import Enum
from typing import NamedTuple, Optional


########################################################################################################################
# Contraption
########################################################################################################################

class CardinalDirection(Enum):
    NORTH = 'N'
    EAST = 'E'
    SOUTH = 'S'
    WEST = 'W'


def translate(width: int, height: int, x: int, y: int, direction: CardinalDirection) -> Optional[tuple[int, int]]:
    assert 0 <= x < width
    assert 0 <= y < height
    if direction == CardinalDirection.NORTH:
        if y > 0:
            return (x, y - 1)
    elif direction == CardinalDirection.SOUTH:
        if y < height - 1:
            return (x, y + 1)
    elif direction == CardinalDirection.EAST:
        if x < width - 1:
            return (x + 1, y)
    elif direction == CardinalDirection.WEST:
        if x > 0:
            return (x - 1, y)
    else:
        raise ValueError(f'Unexpected direction: {direction!r}')
    return None


class Tile(Enum):
    EMPTY_SPACE = '.'
    NE_SW_MIRROR = '/'
    NW_SE_MIRROR = '\\'
    NORTH_SOUTH_SPLITTER = '|'
    EAST_WEST_SPLITTER = '-'


class Contraption(NamedTuple):
    width: int
    height: int
    rows: tuple[tuple[Tile, ...], ...] = ()

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Contraption':
        width = -1
        rows: list[tuple[Tile, ...]] = []
        for (y, line) in enumerate(lines):
            # Ensure width is consistent across lines.
            if y == 0:
                width = len(line)
            elif len(line) != width:
                raise ValueError(f'Width of line {y + 1} differs from line 1 ({len(line)} ≠ {width})')
            rows.append(tuple(Tile(char) for char in line))
        return Contraption(width, y + 1, tuple(rows))

    def __str__(self) -> str:
        return '\n'.join(''.join(tile.value for tile in row) for row in self.rows)

    def simulate(self) -> tuple[tuple[set[CardinalDirection], ...], ...]:
        beams: list[list[set[CardinalDirection]]] = [[set() for _ in row] for row in self.rows]
        beamfronts: list[tuple[int, int, CardinalDirection]] = [(0, 0, CardinalDirection.EAST)]
        while beamfronts:
            next_beamfronts: list[tuple[int, int, CardinalDirection]] = []
            for (x, y, direction) in beamfronts:
                if direction in beams[y][x]:
                    continue
                beams[y][x].add(direction)
                tile = self.rows[y][x]
                if (tile == Tile.EMPTY_SPACE) or \
                   ((tile == Tile.NORTH_SOUTH_SPLITTER) and (direction in {CardinalDirection.NORTH, CardinalDirection.SOUTH})) or \
                   ((tile == Tile.EAST_WEST_SPLITTER) and (direction in {CardinalDirection.EAST, CardinalDirection.WEST})):
                    next_directions = [direction]
                elif tile == Tile.NE_SW_MIRROR:
                    if direction == CardinalDirection.NORTH:
                        next_directions = [CardinalDirection.EAST]
                    elif direction == CardinalDirection.WEST:
                        next_directions = [CardinalDirection.SOUTH]
                    elif direction == CardinalDirection.SOUTH:
                        next_directions = [CardinalDirection.WEST]
                    elif direction == CardinalDirection.EAST:
                        next_directions = [CardinalDirection.NORTH]
                    else:
                        raise ValueError(f'Unexpected direction: {direction!r}')
                elif tile == Tile.NW_SE_MIRROR:
                    if direction == CardinalDirection.NORTH:
                        next_directions = [CardinalDirection.WEST]
                    elif direction == CardinalDirection.EAST:
                        next_directions = [CardinalDirection.SOUTH]
                    elif direction == CardinalDirection.SOUTH:
                        next_directions = [CardinalDirection.EAST]
                    elif direction == CardinalDirection.WEST:
                        next_directions = [CardinalDirection.NORTH]
                    else:
                        raise ValueError(f'Unexpected direction: {direction!r}')
                elif tile == Tile.NORTH_SOUTH_SPLITTER:
                    assert direction in {CardinalDirection.EAST, CardinalDirection.WEST}
                    next_directions = [CardinalDirection.NORTH, CardinalDirection.SOUTH]
                elif tile == Tile.EAST_WEST_SPLITTER:
                    assert direction in {CardinalDirection.NORTH, CardinalDirection.SOUTH}
                    next_directions = [CardinalDirection.EAST, CardinalDirection.WEST]
                else:
                    raise ValueError(f'Unexpected tile at row {y + 1}, column {x + 1}: {tile!r}')
                for next_direction in next_directions:
                    next_coordinates = translate(self.width, self.height, x, y, next_direction)
                    if next_coordinates:
                        next_beamfronts.append((*next_coordinates, next_direction))
            beamfronts = next_beamfronts
        return tuple(tuple(tile for tile in row) for row in beams)


########################################################################################################################
# Part 1
########################################################################################################################

def count_energised_tiles(lines: Iterable[str]) -> int:
    r"""
    >>> count_energised_tiles([
    ...     '.|...\....',
    ...     '|.-.\.....',
    ...     '.....|-...',
    ...     '........|.',
    ...     '..........',
    ...     '.........\\',
    ...     '..../.\\\\..',
    ...     '.-.-/..|..',
    ...     '.|....-|.\\',
    ...     '..//.|....',
    ... ])
    46
    """
    contraption = Contraption.from_lines(lines)
    beams = contraption.simulate()
    return sum(1 for row in beams for tile in row if tile)


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
        print(count_energised_tiles(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
