#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from bisect import insort
from collections.abc import Iterable
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


########################################################################################################################
# Maze
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

    @property
    def normalised_type(self) -> TileType:
        if self.type_ == TileType.STARTING_POSITION:
            if self.to_north is not None:
                if self.to_east is not None:
                    return TileType.NORTH_TO_EAST_PIPE
                elif self.to_south is not None:
                    return TileType.NORTH_TO_SOUTH_PIPE
                elif self.to_west is not None:
                    return TileType.NORTH_TO_WEST_PIPE
            elif self.to_east is not None:
                if self.to_south is not None:
                    return TileType.SOUTH_TO_EAST_PIPE
                elif self.to_west is not None:
                    return TileType.EAST_TO_WEST_PIPE
            elif self.to_south is not None:
                if self.to_west is not None:
                    return TileType.SOUTH_TO_WEST_PIPE
        return self.type_


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


########################################################################################################################
# Part 1
########################################################################################################################

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
# Part 2
########################################################################################################################

def count_tiles_enclosed_by_loop(lines: Iterable[str]) -> int:
    """
    >>> count_tiles_enclosed_by_loop([
    ...     '...........',  # mask spans: []
    ...     '.S-------7.',  # [(1, 9)]
    ...     '.|F-----7|.',  # [(1, 2) (8, 9)]
    ...     '.||.....||.',  # [(1, 2) (8, 9)]
    ...     '.||.....||.',  # [(1, 2) (8, 9)]
    ...     '.|L-7.F-J|.',  # [(1, 4) (6, 9)]
    ...     '.|..|.|..|.',  # [(1, 4) (6, 9)]
    ...     '.L--J.L--J.',  # []
    ...     '...........',  # []
    ... ])
    4
    >>> count_tiles_enclosed_by_loop([
    ...     '..........',
    ...     '.S------7.',
    ...     '.|F----7|.',
    ...     '.||....||.',
    ...     '.||....||.',
    ...     '.|L-7F-J|.',
    ...     '.|..||..|.',
    ...     '.L--JL--J.',
    ...     '..........',
    ... ])
    4
    >>> count_tiles_enclosed_by_loop([
    ...     '.F----7F7F7F7F-7....',
    ...     '.|F--7||||||||FJ....',
    ...     '.||.FJ||||||||L7....',
    ...     'FJL7L7LJLJ||LJ.L-7..',
    ...     'L--J.L7...LJS7F-7L7.',
    ...     '....F-J..F7FJ|L7L7L7',
    ...     '....L7.F7||L7|.L7L7|',
    ...     '.....|FJLJ|FJ|F7|.LJ',
    ...     '....FJL-7.||.||||...',
    ...     '....L---J.LJ.LJLJ...',
    ... ])
    8
    >>> count_tiles_enclosed_by_loop([
    ...     'FF7FSF7F7F7F7F7F---7',
    ...     'L|LJ||||||||||||F--J',
    ...     'FL-7LJLJ||||||LJL-77',
    ...     'F--JF--7||LJLJ7F7FJ-',
    ...     'L---JF-JLJ.||-FJLJJ7',
    ...     '|F|F-JF---7F7-L7L|7|',
    ...     '|FFJF7L7F-JF7|JL---7',
    ...     '7-L-JL7||F7|L7F-7F7|',
    ...     'L.L7LFJ|||||FJL7||LJ',
    ...     'L7JLJL-JLJLJL--JLJ.L',
    ... ])
    10

    >>> count_tiles_enclosed_by_loop([
    ...     '.F-7.',
    ...     'FS.L7',
    ...     '|...|',
    ...     'L7.FJ',
    ...     '.L-J.',
    ... ])
    5
    >>> count_tiles_enclosed_by_loop([
    ...     '.F-7.F-7.',
    ...     'FS.L-J.L7',
    ...     '|.......|',
    ...     'L7.....FJ',
    ...     '.|.....|.',
    ...     'FJ.....L7',
    ...     '|.......|',
    ...     'L7.F-7.FJ',
    ...     '.L-J.L-J.',
    ... ])
    33
    >>> count_tiles_enclosed_by_loop([
    ...     '.F-7.F-7.',
    ...     'FS.|.|.L7',
    ...     '|..L-J..|',
    ...     'L-7...F-J',
    ...     '..|...|..',
    ...     'F-J...L-7',
    ...     '|..F-7..|',
    ...     'L7.|.|.FJ',
    ...     '.L-J.L-J.',
    ... ])
    21
    """
    map_ = Map.from_lines(lines)
    loop = traverse_loop(map_.starting_tile)

    # To calculate the area, we'll scan row by row, left to right. We don't care about horizontal or vertical pipes,
    # only corner pipes, and how they form spans. Essentially, we're building a mask of what's inside the loop and
    # what's outside. If the span touches an edge of a mask span, we add to the mask. If the span overlaps completely
    # with a mask span, we subtract from the mask.
    #
    # Because every piece of pipe is represented, we don't need to worry about interpolating missing rows.
    tiles_by_row: dict[int, list[tuple[int, TileType]]] = {}
    for tile in loop:
        row = tiles_by_row.setdefault(tile.y, [])
        if tile.normalised_type not in {TileType.NORTH_TO_SOUTH_PIPE, TileType.EAST_TO_WEST_PIPE}:
            insort(row, (tile.x, tile.normalised_type))
    spans_by_row: dict[int, list[tuple[int, int]]] = {}
    for (y, row_tiles) in tiles_by_row.items():
        row_spans: list[tuple[int, int]] = []
        span_start: Optional[int] = None
        for (x, tile_type) in row_tiles:
            if tile_type in {TileType.NORTH_TO_EAST_PIPE, TileType.SOUTH_TO_EAST_PIPE}:
                assert span_start is None
                span_start = x
            elif tile_type in {TileType.NORTH_TO_WEST_PIPE, TileType.SOUTH_TO_WEST_PIPE}:
                assert span_start is not None
                row_spans.append((span_start, x))
                span_start = None
            else:
                assert False
        assert span_start is None
        spans_by_row[y] = row_spans
    area = 0
    mask_spans: list[tuple[int, int]] = []
    for j in sorted(spans_by_row.keys()):
        row_spans = spans_by_row[j]
        if not mask_spans:
            mask_spans = row_spans
            continue
        potential_row_area = 0
        for (mask_span_start, mask_span_end) in mask_spans:
            potential_row_area += mask_span_end - mask_span_start - 1
        for row_span in row_spans:
            for (i, mask_span) in enumerate(mask_spans):
                if row_span[1] < mask_span[0]:
                    # Row span is disjoint, strictly to the left of the mask span. Add to mask spans.
                    mask_spans.insert(i, row_span)
                    break
                elif row_span[1] == mask_span[0]:
                    # Row span's right side touches mask span's left side. Extend mask span.
                    mask_spans[i] = (row_span[0], mask_span[1])
                    break
                elif row_span == mask_span:
                    # Row span and mask span are identical. Delete mask span.
                    mask_spans.pop(i)
                    potential_row_area -= row_span[1] - row_span[0] - 1
                    break
                elif mask_span[0] <= row_span[0] and row_span[1] <= mask_span[1]:
                    # Row span is covered by mask span. Subtract mask span.
                    mask_spans.pop(i)
                    if row_span[1] != mask_span[1]:
                        mask_spans.insert(i, (row_span[1], mask_span[1]))
                    if mask_span[0] != row_span[0]:
                        mask_spans.insert(i, (mask_span[0], row_span[0]))
                    potential_row_area -= row_span[1] - row_span[0]
                    if mask_span[0] < row_span[0] and row_span[1] < mask_span[1]:
                        potential_row_area -= 1
                    break
                elif mask_span[1] == row_span[0]:
                    # Row span's left side touches mask span's right side. Extend mask span.
                    mask_spans[i] = (mask_span[0], row_span[1])
                    break
                elif i == len(mask_spans) - 1:
                    # We've exhausted all mask spans. Row span must be disjoint, strictly to the right of the mask span.
                    # Add to mask spans.
                    mask_spans.append(row_span)
                    break
            # Compaction pass.
            i = 0
            while i < (len(mask_spans) - 1):
                mask_span = mask_spans[i]
                next_mask_span = mask_spans[i + 1]
                if next_mask_span[0] == mask_span[1]:
                    mask_spans.pop(i)
                    mask_spans.pop(i)
                    mask_spans.insert(i, (mask_span[0], next_mask_span[1]))
                i += 1
        assert potential_row_area >= 0
        area += potential_row_area
    # We should wind up with an empty mask at the very end.
    assert not mask_spans
    return area


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
    elif args.part == 2:
        print(count_tiles_enclosed_by_loop(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
