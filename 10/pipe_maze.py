#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


########################################################################################################################
# Part 1
########################################################################################################################

class CardinalDirection(Enum):
    NORTH = 'N'
    EAST = 'E'
    SOUTH = 'S'
    WEST = 'W'


class TileType(Enum):
    NORTH_TO_SOUTH_PIPE = '|'
    EAST_TO_WEST_PIPE = '-'
    NORTH_TO_EAST_PIPE = 'L'
    NORTH_TO_WEST_PIPE = 'J'
    SOUTH_TO_WEST_PIPE = '7'
    SOUTH_TO_EAST_PIPE = 'F'
    GROUND = '.'
    STARTING_POSITION = 'S'


TILE_TYPES_TO_VALID_CONNECTION_DIRECTIONS: dict[TileType, set[CardinalDirection]] = {
    TileType.NORTH_TO_SOUTH_PIPE: {CardinalDirection.NORTH, CardinalDirection.SOUTH},
    TileType.EAST_TO_WEST_PIPE: {CardinalDirection.EAST, CardinalDirection.WEST},
    TileType.NORTH_TO_EAST_PIPE: {CardinalDirection.NORTH, CardinalDirection.EAST},
    TileType.NORTH_TO_WEST_PIPE: {CardinalDirection.NORTH, CardinalDirection.WEST},
    TileType.SOUTH_TO_WEST_PIPE: {CardinalDirection.SOUTH, CardinalDirection.WEST},
    TileType.SOUTH_TO_EAST_PIPE: {CardinalDirection.SOUTH, CardinalDirection.EAST},
    TileType.GROUND: set(),
    TileType.STARTING_POSITION: {CardinalDirection.NORTH, CardinalDirection.EAST, CardinalDirection.SOUTH, CardinalDirection.WEST},
}


DIRECTION_TO_DIRECTION: dict[CardinalDirection, CardinalDirection] = {
    CardinalDirection.NORTH: CardinalDirection.SOUTH,
    CardinalDirection.EAST: CardinalDirection.WEST,
    CardinalDirection.SOUTH: CardinalDirection.NORTH,
    CardinalDirection.WEST: CardinalDirection.EAST,
}


@dataclass(eq=False)
class Tile:
    type_: TileType
    x: int
    y: int
    to_north: Optional['Tile'] = field(default=None, init=False)
    to_east: Optional['Tile'] = field(default=None, init=False)
    to_south: Optional['Tile'] = field(default=None, init=False)
    to_west: Optional['Tile'] = field(default=None, init=False)

    def maybe_connect(self, from_direction: CardinalDirection, tile: 'Tile') -> bool:
        if from_direction not in TILE_TYPES_TO_VALID_CONNECTION_DIRECTIONS[self.type_]:
            return False
        if sum((self.to_north is not None, self.to_east is not None, self.to_south is not None, self.to_west is not None)) >= 2:
            raise ValueError(f'Attempted to connect {tile!r} to {self!r}, but the latter is already fully connected')
        if from_direction == CardinalDirection.NORTH:
            self.to_north = tile
        elif from_direction == CardinalDirection.EAST:
            self.to_east = tile
        elif from_direction == CardinalDirection.SOUTH:
            self.to_south = tile
        elif from_direction == CardinalDirection.WEST:
            self.to_west = tile
        else:
            raise ValueError(f'Unexpected direction {from_direction!r}')
        return True

    def next_tile(self, prev_tile: Optional['Tile']) -> Optional['Tile']:
        if self.type_ == TileType.GROUND:
            raise ValueError(f'Tile {self!r} is not a pipe')
        next_tiles = {tile for tile in (self.to_north, self.to_east, self.to_south, self.to_west) if tile is not None}
        if prev_tile is None:
            return next_tiles.pop()
        next_tiles.remove(prev_tile)
        return next_tiles.pop()


@dataclass
class Map:
    width: int
    height: int
    tiles: tuple[tuple[Tile, ...], ...]
    starting_tile: Tile

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Map':
        width = -1
        height = 0
        tiles: list[tuple[Tile, ...]] = []
        starting_tile: Optional[Tile] = None

        for (y, line) in enumerate(lines):
            # Ensure width is consistent across lines.
            if y == 0:
                width = len(line)
            elif len(line) != width:
                raise ValueError(f'Width of line {y + 1} differs from line 1 ({len(line)} ≠ {width})')

            row_tiles: list[Tile] = []
            for (x, char) in enumerate(line):
                tile = Tile(TileType(char), x, y)
                if tile.type_ == TileType.STARTING_POSITION:
                    if starting_tile is not None:
                        raise ValueError(f'Encountered a second starting tile {tile!r}; first starting tile was {starting_tile!r}')
                    starting_tile = tile
                possible_directions = TILE_TYPES_TO_VALID_CONNECTION_DIRECTIONS[tile.type_] & {CardinalDirection.NORTH, CardinalDirection.WEST}
                for direction in possible_directions:
                    other_tile: Optional[Tile] = None
                    if direction == CardinalDirection.NORTH:
                        if y > 0:
                            other_tile = tiles[y - 1][x]
                    elif direction == CardinalDirection.WEST:
                        if x > 0:
                            other_tile = row_tiles[x - 1]
                    else:
                        raise ValueError(f'Unexpected direction {direction!r}')
                    if other_tile and other_tile.maybe_connect(DIRECTION_TO_DIRECTION[direction], tile):
                        assert tile.maybe_connect(direction, other_tile)
                row_tiles.append(tile)
            tiles.append(tuple(row_tiles))

        assert starting_tile is not None
        return Map(width, height, tuple(tiles), starting_tile)


def traverse_loop(starting_tile: Tile) -> tuple[Tile, ...]:
    tiles = [starting_tile]
    prev_tile = None
    tile = starting_tile
    while True:
        tile_ = tile.next_tile(prev_tile)
        if tile_ is None:
            raise ValueError(f'Encountered dead end when attempting to traverse loop: {tiles!r}')
        if tile_ == starting_tile:
            break
        tiles.append(tile_)
        prev_tile = tile
        tile = tile_
    return tuple(tiles)


def count_steps_from_starting_to_farthest_position(lines: Iterable[str]) -> int:
    """
    >>> count_steps_from_starting_to_farthest_position([
    ...     '.....',
    ...     '.S-7.',
    ...     '.|.|.',
    ...     '.L-J.',
    ...     '.....',
    ... ])
    4
    >>> count_steps_from_starting_to_farthest_position([
    ...     '-L|F7',
    ...     '7S-7|',
    ...     'L|7||',
    ...     '-L-J|',
    ...     'L|-JF',
    ... ])
    4
    >>> count_steps_from_starting_to_farthest_position([
    ...     '..F7.',
    ...     '.FJ|.',
    ...     'SJ.L7',
    ...     '|F--J',
    ...     'LJ...',
    ... ])
    8
    >>> count_steps_from_starting_to_farthest_position([
    ...     '7-F7-',
    ...     '.FJ|7',
    ...     'SJLL7',
    ...     '|F--J',
    ...     'LJ.LJ',
    ... ])
    8
    """
    map_ = Map.from_lines(lines)
    loop = traverse_loop(map_.starting_tile)
    assert len(loop) % 2 == 0
    return len(loop) // 2


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
        print(count_steps_from_starting_to_farthest_position(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
