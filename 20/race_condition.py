#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable, Iterator
from enum import Enum
from typing import NamedTuple, Optional


########################################################################################################################
# CPU
########################################################################################################################

class Coordinate(NamedTuple):
    x: int
    y: int

    def __str__(self) -> 'str':
        return f'({self.x}, {self.y})'


class Tile(Enum):
    EMPTY_SPACE = '.'
    WALL = '#'
    START = 'S'
    END = 'E'


class Racetrack(NamedTuple):
    rows: tuple[tuple[Tile, ...], ...]
    path: tuple[Coordinate, ...]

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Racetrack':
        width = -1
        mutable_rows: list[tuple[Tile, ...]] = []
        start_position: Optional[Coordinate] = None
        end_position: Optional[Coordinate] = None
        for (y, line) in enumerate(lines):
            # Ensure width is consistent across lines.
            if y == 0:
                width = len(line)
            elif len(line) != width:
                raise ValueError(f'Width of line {y + 1} differs from line 1 ({len(line)} ≠ {width})')
            mutable_row: list[Tile] = []
            for (x, char) in enumerate(line):
                tile = Tile(char)
                if tile == Tile.START:
                    if start_position is not None:
                        raise ValueError(f'Encountered a second start tile at {Coordinate(x, y)}; first start tile was at {start_position}')
                    start_position = Coordinate(x, y)
                    tile = Tile.EMPTY_SPACE
                elif tile == Tile.END:
                    if end_position is not None:
                        raise ValueError(f'Encountered a second end tile at {Coordinate(x, y)}; first end tile was at {end_position}')
                    end_position = Coordinate(x, y)
                    tile = Tile.EMPTY_SPACE
                mutable_row.append(tile)
            mutable_rows.append(tuple(mutable_row))
        if start_position is None:
            raise ValueError('Map is missing a start tile')
        if end_position is None:
            raise ValueError('Map is missing an end tile')
        rows = tuple(mutable_rows)

        prev_position: Optional[Coordinate] = None
        position = start_position
        mutable_path: list[Coordinate] = [start_position]
        while position != end_position:
            possible_positions = set(neighbours(rows, position))
            if prev_position is not None:
                possible_positions.remove(prev_position)
            assert len(possible_positions) == 1
            prev_position = position
            position = possible_positions.pop()
            mutable_path.append(position)
        path = tuple(mutable_path)

        return Racetrack(rows, path)

    @property
    def duration(self) -> int:
        """
        >>> Racetrack.from_lines([
        ...     '###############',
        ...     '#...#...#.....#',
        ...     '#.#.#.#.#.###.#',
        ...     '#S#...#.#.#...#',
        ...     '#######.#.#.###',
        ...     '#######.#.#...#',
        ...     '#######.#.###.#',
        ...     '###..E#...#...#',
        ...     '###.#######.###',
        ...     '#...###...#...#',
        ...     '#.#####.#.###.#',
        ...     '#.#...#.#.#...#',
        ...     '#.#.#.#.#.#.###',
        ...     '#...#...#...###',
        ...     '###############',
        ... ]).duration
        84
        """
        assert len(self.path) > 0
        return len(self.path) - 1

    def two_ps_cheats(self, min_savings_duration: int) -> Iterator[tuple[Coordinate, Coordinate, int]]:
        """
        >>> from collections import Counter
        >>> sorted(Counter(savings_duration for (_, _, savings_duration) in Racetrack.from_lines([
        ...     '###############',
        ...     '#...#...#.....#',
        ...     '#.#.#.#.#.###.#',
        ...     '#S#...#.#.#...#',
        ...     '#######.#.#.###',
        ...     '#######.#.#...#',
        ...     '#######.#.###.#',
        ...     '###..E#...#...#',
        ...     '###.#######.###',
        ...     '#...###...#...#',
        ...     '#.#####.#.###.#',
        ...     '#.#...#.#.#...#',
        ...     '#.#.#.#.#.#.###',
        ...     '#...#...#...###',
        ...     '###############',
        ... ]).two_ps_cheats(1)).items())
        [(2, 14), (4, 14), (6, 2), (8, 4), (10, 2), (12, 3), (20, 1), (36, 1), (38, 1), (40, 1), (64, 1)]
        """
        positions_ahead = {position: i for (i, position) in enumerate(self.path)}
        for (i, start_position) in enumerate(self.path):
            del positions_ahead[start_position]
            for end_position in partitioned_neighbours(self.rows, start_position):
                if end_position not in positions_ahead:
                    continue
                j = positions_ahead[end_position]
                savings_duration = j - i - 2
                if savings_duration < min_savings_duration:
                    continue
                yield (start_position, end_position, savings_duration)

    def twenty_ps_cheats(self, min_savings_duration: int) -> Iterator[tuple[Coordinate, Coordinate, int]]:
        """
        >>> from collections import Counter
        >>> sorted(Counter(savings_duration for (_, _, savings_duration) in Racetrack.from_lines([
        ...     '###############',
        ...     '#...#...#.....#',
        ...     '#.#.#.#.#.###.#',
        ...     '#S#...#.#.#...#',
        ...     '#######.#.#.###',
        ...     '#######.#.#...#',
        ...     '#######.#.###.#',
        ...     '###..E#...#...#',
        ...     '###.#######.###',
        ...     '#...###...#...#',
        ...     '#.#####.#.###.#',
        ...     '#.#...#.#.#...#',
        ...     '#.#.#.#.#.#.###',
        ...     '#...#...#...###',
        ...     '###############',
        ... ]).twenty_ps_cheats(50)).items())
        [(50, 32), (52, 31), (54, 29), (56, 39), (58, 25), (60, 23), (62, 20), (64, 19), (66, 12), (68, 14), (70, 12), (72, 22), (74, 4), (76, 3)]
        """
        positions_ahead = {position: i for (i, position) in enumerate(self.path)}
        for (i, start_position) in enumerate(self.path):
            del positions_ahead[start_position]
            # O(n²) ain't the prettiest, but it gets the job done.
            for (end_position, j) in positions_ahead.items():
                cheat_duration = manhattan_distance(start_position, end_position)
                if cheat_duration > 20:
                    continue
                savings_duration = j - i - cheat_duration
                if savings_duration < min_savings_duration:
                    continue
                yield (start_position, end_position, savings_duration)


def neighbours(rows: tuple[tuple[Tile, ...], ...], position: Coordinate) -> Iterator[Coordinate]:
    assert (height := len(rows)) >= 1
    assert (width := len(rows[0])) >= 1
    (x, y) = position
    if ((new_y := y - 1) >= 0) and (rows[new_y][x] == Tile.EMPTY_SPACE):
        yield Coordinate(x, new_y)
    if ((new_y := y + 1) < height) and (rows[new_y][x] == Tile.EMPTY_SPACE):
        yield Coordinate(x, new_y)
    if ((new_x := x - 1) >= 0) and (rows[y][new_x] == Tile.EMPTY_SPACE):
        yield Coordinate(new_x, y)
    if ((new_x := x + 1) < width) and (rows[y][new_x] == Tile.EMPTY_SPACE):
        yield Coordinate(new_x, y)


def partitioned_neighbours(rows: tuple[tuple[Tile, ...], ...], position: Coordinate) -> Iterator[Coordinate]:
    assert (height := len(rows)) >= 1
    assert (width := len(rows[0])) >= 1
    (x, y) = position
    if ((new_y := y - 2) >= 0) and (rows[new_y][x] == Tile.EMPTY_SPACE) and (rows[y - 1][x] == Tile.WALL):
        yield Coordinate(x, new_y)
    if ((new_y := y + 2) < height) and (rows[new_y][x] == Tile.EMPTY_SPACE) and (rows[y + 1][x] == Tile.WALL):
        yield Coordinate(x, new_y)
    if ((new_x := x - 2) >= 0) and (rows[y][new_x] == Tile.EMPTY_SPACE) and (rows[y][x - 1] == Tile.WALL):
        yield Coordinate(new_x, y)
    if ((new_x := x + 2) < width) and (rows[y][new_x] == Tile.EMPTY_SPACE) and (rows[y][x + 1] == Tile.WALL):
        yield Coordinate(new_x, y)


def manhattan_distance(start_position: Coordinate, end_position: Coordinate) -> int:
    return abs(end_position.x - start_position.x) + abs(end_position.y - start_position.y)


########################################################################################################################
# Part 1
########################################################################################################################

def count_two_ps_cheats_saving_at_least_100_ps(lines: Iterable[str]) -> int:
    racetrack = Racetrack.from_lines(lines)
    return sum(1 for _ in racetrack.two_ps_cheats(100))


########################################################################################################################
# Part 2
########################################################################################################################

def count_twenty_ps_cheats_saving_at_least_100_ps(lines: Iterable[str]) -> int:
    racetrack = Racetrack.from_lines(lines)
    return sum(1 for _ in racetrack.twenty_ps_cheats(100))


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
        print(count_two_ps_cheats_saving_at_least_100_ps(lines))
    elif args.part == 2:
        print(count_twenty_ps_cheats_saving_at_least_100_ps(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
