#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable, Iterator
from enum import Enum
from typing import NamedTuple, Optional


########################################################################################################################
# Map
########################################################################################################################

class Coordinate(NamedTuple):
    x: int
    y: int


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
    PATH = '.'
    FOREST = '#'
    NORTH_FACING_SLOPE = '^'
    EAST_FACING_SLOPE = '>'
    SOUTH_FACING_SLOPE = 'v'
    WEST_FACING_SLOPE = '<'


SLOPE_TO_CARDINAL_DIRECTION = {
    Tile.NORTH_FACING_SLOPE: CardinalDirection.NORTH,
    Tile.EAST_FACING_SLOPE: CardinalDirection.EAST,
    Tile.SOUTH_FACING_SLOPE: CardinalDirection.SOUTH,
    Tile.WEST_FACING_SLOPE: CardinalDirection.WEST,
}


class Map(NamedTuple):
    width: int
    height: int
    rows: tuple[tuple[Tile, ...], ...]
    starting_position: Coordinate
    ending_position: Coordinate
    paths: dict[Coordinate, set[tuple[Coordinate, Coordinate, tuple[Coordinate, ...]]]]

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Map':
        width = -1
        rows: list[tuple[Tile, ...]] = []
        for (y, line) in enumerate(lines):
            # Ensure width is consistent across lines.
            if y == 0:
                width = len(line)
                assert width >= 3
            elif len(line) != width:
                raise ValueError(f'Width of line {y + 1} differs from line 1 ({len(line)} ≠ {width})')
            row = tuple(Tile(char) for char in line)
            if y == 0:
                assert row == (Tile.FOREST, Tile.PATH) + ((Tile.FOREST,) * (width - 2))
            else:
                assert row[0] == row[-1] == Tile.FOREST
            rows.append(row)
        height = y + 1
        starting_position = Coordinate(1, 0)
        assert row == ((Tile.FOREST,) * (width - 2)) + (Tile.PATH, Tile.FOREST)
        ending_position = Coordinate(width - 2, y)

        paths: dict[Coordinate, set[tuple[Coordinate, Coordinate, tuple[Coordinate, ...]]]] = {}
        explored_paths: set[tuple[Coordinate, CardinalDirection]] = set()
        paths_to_explore: list[tuple[Coordinate, CardinalDirection]] = [(starting_position, CardinalDirection.SOUTH)]
        while paths_to_explore:
            (starting_path_position, prev_path_direction) = paths_to_explore.pop(0)
            if (starting_path_position, prev_path_direction) in explored_paths:
                continue
            explored_paths.add((starting_path_position, prev_path_direction))
            prev_path_position = starting_path_position
            path_positions: list[Coordinate] = []
            while True:
                path_position = translate(width, height, prev_path_position, prev_path_direction)
                assert path_position is not None
                path_positions.append(path_position)
                path_tile = rows[path_position.y][path_position.x]
                assert path_tile in {Tile.PATH, Tile.NORTH_FACING_SLOPE, Tile.EAST_FACING_SLOPE, Tile.SOUTH_FACING_SLOPE, Tile.WEST_FACING_SLOPE}

                if path_position == ending_position:
                    paths.setdefault(starting_path_position, set()).add((starting_path_position, path_position, tuple(path_positions)))
                    break

                path_directions = set(CardinalDirection) - {prev_path_direction.reverse}
                for path_direction in list(path_directions):
                    next_path_position = translate(width, height, path_position, path_direction)
                    if next_path_position is None:
                        path_directions.remove(path_direction)
                        continue
                    next_path_tile = rows[next_path_position.y][next_path_position.x]
                    if next_path_tile == Tile.FOREST:
                        path_directions.remove(path_direction)
                        continue
                    if next_path_tile in {Tile.NORTH_FACING_SLOPE, Tile.EAST_FACING_SLOPE, Tile.SOUTH_FACING_SLOPE, Tile.WEST_FACING_SLOPE}:
                        if SLOPE_TO_CARDINAL_DIRECTION[next_path_tile] == path_direction.reverse:
                            # This path is about to have us walk backwards. As an optimisation, we _could_ finish
                            # following the path and just remember the polarity.
                            path_directions.remove(path_direction)
                            continue
                    else:
                        assert next_path_tile == Tile.PATH
                if len(path_directions) == 0:
                    # We have no valid ways forward. Abandon this path.
                    break
                if len(path_directions) > 1:
                    # We're at a junction. Time to finish this path segment, and start some new paths to explore.
                    paths.setdefault(starting_path_position, set()).add((starting_path_position, path_position, tuple(path_positions)))
                    for path_direction in path_directions:
                        paths_to_explore.append((path_position, path_direction))
                    break
                assert len(path_directions) == 1
                prev_path_position = path_position
                prev_path_direction = path_directions.pop()

        return Map(width, height, tuple(rows), starting_position, ending_position, paths)

    def count_steps_for_longest_hiking_trail(self) -> int:
        def explore(visited_path_positions: set[Coordinate], starting_path_position: Coordinate) -> Iterator[set[Coordinate]]:
            assert starting_path_position in self.paths
            for (_, ending_path_position, path_positions_sequence) in self.paths[starting_path_position]:
                path_positions = set(path_positions_sequence)
                if visited_path_positions & path_positions:
                    # New path traverses previously visited tiles; abandon.
                    continue
                combined_path_positions = visited_path_positions | path_positions
                if ending_path_position == self.ending_position:
                    yield combined_path_positions
                if ending_path_position not in self.paths:
                    continue
                yield from explore(combined_path_positions, ending_path_position)
        return max(len(positions) for positions in explore(set(), self.starting_position))


########################################################################################################################
# Part 1
########################################################################################################################

def count_steps_for_longest_hiking_trail(lines: Iterable[str]) -> int:
    """
    >>> count_steps_for_longest_hiking_trail([
    ...     '#.#####################',
    ...     '#.......#########...###',
    ...     '#######.#########.#.###',
    ...     '###.....#.>.>.###.#.###',
    ...     '###v#####.#v#.###.#.###',
    ...     '###.>...#.#.#.....#...#',
    ...     '###v###.#.#.#########.#',
    ...     '###...#.#.#.......#...#',
    ...     '#####.#.#.#######.#.###',
    ...     '#.....#.#.#.......#...#',
    ...     '#.#####.#.#.#########v#',
    ...     '#.#...#...#...###...>.#',
    ...     '#.#.#v#######v###.###v#',
    ...     '#...#.>.#...>.>.#.###.#',
    ...     '#####v#.#.###v#.#.###.#',
    ...     '#.....#...#...#.#.#...#',
    ...     '#.#########.###.#.#.###',
    ...     '#...###...#...#...#.###',
    ...     '###.###.#.###v#####v###',
    ...     '#...#...#.#.>.>.#.>.###',
    ...     '#.###.###.#.###.#.#v###',
    ...     '#.....###...###...#...#',
    ...     '#####################.#',
    ... ])
    94
    """
    map_ = Map.from_lines(lines)
    return map_.count_steps_for_longest_hiking_trail()


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
        print(count_steps_for_longest_hiking_trail(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
