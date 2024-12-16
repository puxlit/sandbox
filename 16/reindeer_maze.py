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

    def find_lowest_score_paths(self) -> tuple[int, set[Coordinate]]:
        """
        >>> (lowest_score, positions_along_paths) = Maze.from_lines([
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
        ... ]).find_lowest_score_paths()
        >>> lowest_score
        7036
        >>> sorted(positions_along_paths)
        [Coordinate(x=1, y=9), Coordinate(x=1, y=10), Coordinate(x=1, y=11), Coordinate(x=1, y=12), Coordinate(x=1, y=13), Coordinate(x=2, y=9), Coordinate(x=2, y=11), Coordinate(x=3, y=7), Coordinate(x=3, y=8), Coordinate(x=3, y=9), Coordinate(x=3, y=10), Coordinate(x=3, y=11), Coordinate(x=4, y=7), Coordinate(x=4, y=11), Coordinate(x=5, y=7), Coordinate(x=5, y=8), Coordinate(x=5, y=9), Coordinate(x=5, y=10), Coordinate(x=5, y=11), Coordinate(x=6, y=7), Coordinate(x=7, y=7), Coordinate(x=8, y=7), Coordinate(x=9, y=7), Coordinate(x=10, y=7), Coordinate(x=11, y=7), Coordinate(x=11, y=8), Coordinate(x=11, y=9), Coordinate(x=11, y=10), Coordinate(x=11, y=11), Coordinate(x=11, y=12), Coordinate(x=11, y=13), Coordinate(x=12, y=13), Coordinate(x=13, y=1), Coordinate(x=13, y=2), Coordinate(x=13, y=3), Coordinate(x=13, y=4), Coordinate(x=13, y=5), Coordinate(x=13, y=6), Coordinate(x=13, y=7), Coordinate(x=13, y=8), Coordinate(x=13, y=9), Coordinate(x=13, y=10), Coordinate(x=13, y=11), Coordinate(x=13, y=12), Coordinate(x=13, y=13)]
        >>> (lowest_score, positions_along_paths) = Maze.from_lines([
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
        ... ]).find_lowest_score_paths()
        >>> lowest_score
        11048
        >>> sorted(positions_along_paths)
        [Coordinate(x=1, y=5), Coordinate(x=1, y=6), Coordinate(x=1, y=7), Coordinate(x=1, y=8), Coordinate(x=1, y=9), Coordinate(x=1, y=10), Coordinate(x=1, y=11), Coordinate(x=1, y=12), Coordinate(x=1, y=13), Coordinate(x=1, y=14), Coordinate(x=1, y=15), Coordinate(x=2, y=5), Coordinate(x=3, y=5), Coordinate(x=3, y=6), Coordinate(x=3, y=7), Coordinate(x=3, y=8), Coordinate(x=3, y=9), Coordinate(x=3, y=10), Coordinate(x=3, y=11), Coordinate(x=3, y=12), Coordinate(x=3, y=13), Coordinate(x=3, y=14), Coordinate(x=3, y=15), Coordinate(x=4, y=15), Coordinate(x=5, y=11), Coordinate(x=5, y=12), Coordinate(x=5, y=13), Coordinate(x=5, y=14), Coordinate(x=5, y=15), Coordinate(x=6, y=11), Coordinate(x=6, y=13), Coordinate(x=7, y=9), Coordinate(x=7, y=10), Coordinate(x=7, y=11), Coordinate(x=7, y=13), Coordinate(x=8, y=9), Coordinate(x=8, y=13), Coordinate(x=9, y=9), Coordinate(x=9, y=13), Coordinate(x=10, y=9), Coordinate(x=10, y=13), Coordinate(x=11, y=7), Coordinate(x=11, y=8), Coordinate(x=11, y=9), Coordinate(x=11, y=11), Coordinate(x=11, y=12), Coordinate(x=11, y=13), Coordinate(x=12, y=7), Coordinate(x=12, y=11), Coordinate(x=13, y=7), Coordinate(x=13, y=9), Coordinate(x=13, y=10), Coordinate(x=13, y=11), Coordinate(x=14, y=7), Coordinate(x=14, y=9), Coordinate(x=15, y=1), Coordinate(x=15, y=2), Coordinate(x=15, y=3), Coordinate(x=15, y=4), Coordinate(x=15, y=5), Coordinate(x=15, y=6), Coordinate(x=15, y=7), Coordinate(x=15, y=8), Coordinate(x=15, y=9)]

        >>> (lowest_score, positions_along_paths) = Maze.from_lines([
        ...     '#######',
        ...     '#.....#',
        ...     '#S#.#E#',
        ...     '#.....#',
        ...     '#######',
        ... ]).find_lowest_score_paths()
        >>> lowest_score
        3006
        >>> sorted(positions_along_paths)
        [Coordinate(x=1, y=1), Coordinate(x=1, y=2), Coordinate(x=1, y=3), Coordinate(x=2, y=1), Coordinate(x=2, y=3), Coordinate(x=3, y=1), Coordinate(x=3, y=3), Coordinate(x=4, y=1), Coordinate(x=4, y=3), Coordinate(x=5, y=1), Coordinate(x=5, y=2), Coordinate(x=5, y=3)]
        """
        start_node = (self.start_position, self.start_orientation)
        start_h_score = manhattan_distance(self.start_position, self.end_position)

        prev_nodes: dict[tuple[Coordinate, Orientation], set[tuple[Coordinate, Orientation]]] = {}
        g_scores: dict[tuple[Coordinate, Orientation], int] = {start_node: 0}
        f_scores: dict[tuple[Coordinate, Orientation], int] = {start_node: start_h_score}
        queue: deque[tuple[int, Coordinate, Orientation]] = deque([(start_h_score, *start_node)])
        lowest_score: Optional[int] = None
        end_nodes: set[tuple[Coordinate, Orientation]] = set()
        while queue:
            # 에이스타, 에이스타
            # 에이스타, 에이스타
            # 에이스타, 에이스타
            # Uh, uh-huh uh-huh
            (_, position, orientation) = queue.popleft()
            node = (position, orientation)

            if (position == self.end_position) and ((lowest_score is None) or (g_scores[node] == lowest_score)):
                end_nodes.add(node)
                lowest_score = g_scores[node]

            g_score = g_scores[node]
            for (next_position, next_orientation, edge_score) in self.neighbours(position, orientation):
                next_node = (next_position, next_orientation)
                next_g_score = g_score + edge_score
                if (lowest_score is not None) and (next_g_score > lowest_score):
                    continue
                if (next_node not in g_scores) or (next_g_score < g_scores[next_node]):
                    prev_nodes[next_node] = {node}
                    g_scores[next_node] = next_g_score
                    if next_node in f_scores:
                        expected_queue_item = (f_scores[next_node], *next_node)
                        i = bisect_left(queue, expected_queue_item)
                        assert queue[i] == expected_queue_item
                        del queue[i]
                    next_f_score = next_g_score + manhattan_distance(next_position, self.end_position)
                    f_scores[next_node] = next_f_score
                    insort_right(queue, (next_f_score, *next_node))
                elif next_g_score == g_scores[next_node]:
                    prev_nodes[next_node].add(node)
        assert lowest_score is not None
        assert len(end_nodes) > 0

        # Reconstruct paths with lowest score.
        positions_along_paths: set[Coordinate] = set()
        nodes_to_follow: deque[tuple[Coordinate, Orientation]] = deque(end_nodes)
        while nodes_to_follow:
            node = nodes_to_follow.popleft()
            positions_along_paths.add(node[0])
            if node in prev_nodes:
                nodes_to_follow.extend(prev_nodes[node])

        return (lowest_score, positions_along_paths)


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
    (lowest_score, _) = maze.find_lowest_score_paths()
    return lowest_score


########################################################################################################################
# Part 2
########################################################################################################################

def count_positions_along_lowest_score_paths(lines: Iterable[str]) -> int:
    """
    >>> count_positions_along_lowest_score_paths([
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
    45
    >>> count_positions_along_lowest_score_paths([
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
    64
    """
    maze = Maze.from_lines(lines)
    (_, positions_along_paths) = maze.find_lowest_score_paths()
    return len(positions_along_paths)


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
    elif args.part == 2:
        print(count_positions_along_lowest_score_paths(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
