#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from bisect import bisect_left, insort_right
from collections import deque
from collections.abc import Iterable, Iterator
from enum import Enum, IntEnum
from typing import NamedTuple, Optional

from typing_extensions import assert_never


########################################################################################################################
# Maze
########################################################################################################################

STEP_SCORE = 1
TURN_SCORE = 1000


class Coordinate(NamedTuple):
    x: int
    y: int

    def __str__(self) -> 'str':
        return f'({self.x}, {self.y})'


class Orientation(IntEnum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

    @property
    def reverse(self) -> 'Orientation':
        if self == Orientation.NORTH:
            return Orientation.SOUTH
        elif self == Orientation.SOUTH:
            return Orientation.NORTH
        elif self == Orientation.EAST:
            return Orientation.WEST
        elif self == Orientation.WEST:
            return Orientation.EAST
        assert_never(self)


class Tile(Enum):
    EMPTY_SPACE = '.'
    WALL = '#'
    START = 'S'
    END = 'E'


class Maze(NamedTuple):
    max_x: int
    max_y: int
    rows: tuple[tuple[Tile, ...], ...]
    start_position: Coordinate
    start_orientation: Orientation
    end_position: Coordinate

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Maze':
        width = -1
        rows: list[tuple[Tile, ...]] = []
        start_position: Optional[Coordinate] = None
        end_position: Optional[Coordinate] = None
        for (y, line) in enumerate(lines):
            # Ensure width is consistent across lines.
            if y == 0:
                width = len(line)
            elif len(line) != width:
                raise ValueError(f'Width of line {y + 1} differs from line 1 ({len(line)} ≠ {width})')
            row: list[Tile] = []
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
                row.append(tile)
            rows.append(tuple(row))
        if start_position is None:
            raise ValueError('Map is missing a start tile')
        if end_position is None:
            raise ValueError('Map is missing an end tile')
        return Maze(width - 1, y, tuple(rows), start_position, Orientation.EAST, end_position)

    def neighbours(self, position: Coordinate, orientation: Orientation) -> Iterator[tuple[Coordinate, Orientation, int]]:
        if (position.y > 0) and (self.rows[position.y - 1][position.x] == Tile.EMPTY_SPACE) and (orientation.reverse != Orientation.NORTH):
            score = STEP_SCORE if (orientation == Orientation.NORTH) else (TURN_SCORE + STEP_SCORE)
            yield (Coordinate(position.x, position.y - 1), Orientation.NORTH, score)
        if (position.y < self.max_y) and (self.rows[position.y + 1][position.x] == Tile.EMPTY_SPACE) and (orientation.reverse != Orientation.SOUTH):
            score = STEP_SCORE if (orientation == Orientation.SOUTH) else (TURN_SCORE + STEP_SCORE)
            yield (Coordinate(position.x, position.y + 1), Orientation.SOUTH, score)
        if (position.x > 0) and (self.rows[position.y][position.x - 1] == Tile.EMPTY_SPACE) and (orientation.reverse != Orientation.WEST):
            score = STEP_SCORE if (orientation == Orientation.WEST) else (TURN_SCORE + STEP_SCORE)
            yield (Coordinate(position.x - 1, position.y), Orientation.WEST, score)
        if (position.x < self.max_x) and (self.rows[position.y][position.x + 1] == Tile.EMPTY_SPACE) and (orientation.reverse != Orientation.EAST):
            score = STEP_SCORE if (orientation == Orientation.EAST) else (TURN_SCORE + STEP_SCORE)
            yield (Coordinate(position.x + 1, position.y), Orientation.EAST, score)

    def find_lowest_score_path(self) -> tuple[tuple[Orientation, ...], int]:
        start_node = (self.start_position, self.start_orientation)
        start_h_score = manhattan_distance(self.start_position, self.end_position)

        prev_node: dict[tuple[Coordinate, Orientation], tuple[Coordinate, Orientation]] = {}
        g_scores: dict[tuple[Coordinate, Orientation], int] = {start_node: 0}
        f_scores: dict[tuple[Coordinate, Orientation], int] = {start_node: start_h_score}
        queue: deque[tuple[int, Coordinate, Orientation]] = deque([(start_h_score, *start_node)])
        end_node: Optional[tuple[Coordinate, Orientation]] = None
        while queue:
            # 에이스타, 에이스타
            # 에이스타, 에이스타
            # 에이스타, 에이스타
            # Uh, uh-huh uh-huh
            (_, position, orientation) = queue.popleft()
            node = (position, orientation)

            if position == self.end_position:
                end_node = node
                break

            g_score = g_scores[node]
            for (next_position, next_orientation, edge_score) in self.neighbours(position, orientation):
                next_node = (next_position, next_orientation)
                next_g_score = g_score + edge_score
                if (next_node not in g_scores) or (next_g_score < g_scores[next_node]):
                    prev_node[next_node] = node
                    g_scores[next_node] = next_g_score
                    if next_node in f_scores:
                        expected_queue_item = (f_scores[next_node], *next_node)
                        i = bisect_left(queue, expected_queue_item)
                        assert queue[i] == expected_queue_item
                        del queue[i]
                    next_f_score = next_g_score + manhattan_distance(next_position, self.end_position)
                    f_scores[next_node] = next_f_score
                    insort_right(queue, (next_f_score, *next_node))
        assert end_node is not None

        path: deque[Orientation] = deque([])
        node = end_node
        while node[0] != self.start_position:
            path.appendleft(node[1])
            node = prev_node[node]

        return (tuple(path), g_scores[end_node])


def manhattan_distance(start_position: Coordinate, end_position: Coordinate) -> int:
    return abs(end_position.x - start_position.x) + abs(end_position.y - start_position.y)


########################################################################################################################
# Part 1
########################################################################################################################

def calculate_lowest_score_path(lines: Iterable[str]) -> int:
    """
    >>> calculate_lowest_score_path([
    ...     '###############',
    ...     '#.......#....E#',
    ...     '#.#.###.#.###.#',
    ...     '#.....#.#...#.#',
    ...     '#.###.#####.#.#',
    ...     '#.#.#.......#.#',
    ...     '#.#.#####.###.#',
    ...     '#...........#.#',
    ...     '###.#.#####.#.#',
    ...     '#...#.....#.#.#',
    ...     '#.#.#.###.#.#.#',
    ...     '#.....#...#.#.#',
    ...     '#.###.#.#.#.#.#',
    ...     '#S..#.....#...#',
    ...     '###############',
    ... ])
    7036
    >>> calculate_lowest_score_path([
    ...     '#################',
    ...     '#...#...#...#..E#',
    ...     '#.#.#.#.#.#.#.#.#',
    ...     '#.#.#.#...#...#.#',
    ...     '#.#.#.#.###.#.#.#',
    ...     '#...#.#.#.....#.#',
    ...     '#.#.#.#.#.#####.#',
    ...     '#.#...#.#.#.....#',
    ...     '#.#.#####.#.###.#',
    ...     '#.#.#.......#...#',
    ...     '#.#.###.#####.###',
    ...     '#.#.#...#.....#.#',
    ...     '#.#.#.#####.###.#',
    ...     '#.#.#.........#.#',
    ...     '#.#.#.#########.#',
    ...     '#S#.............#',
    ...     '#################',
    ... ])
    11048
    """
    maze = Maze.from_lines(lines)
    (_, score) = maze.find_lowest_score_path()
    return score


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
        print(calculate_lowest_score_path(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
