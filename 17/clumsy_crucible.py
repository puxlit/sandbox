#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from enum import Enum
from heapq import heappop, heappush
from itertools import groupby
from typing import NamedTuple, Optional


########################################################################################################################
# Contraption
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


@dataclass(order=True, frozen=True)
class Path:
    start: Coordinate = field(hash=True, compare=False)
    end: Coordinate = field(hash=True, compare=False)
    directions: tuple[CardinalDirection, ...] = field(hash=True, compare=False)
    cost: int = field(hash=True, compare=False)
    heuristic_cost: int = field(hash=True, compare=False)
    total_cost: int = field(init=False, hash=True, compare=True)

    def __post_init__(self) -> None:
        object.__setattr__(self, 'total_cost', self.cost + self.heuristic_cost)


def manhattan_distance(a: Coordinate, b: Coordinate) -> int:
    return abs(a.x - b.x) + abs(a.y - b.y)


def translate(width: int, height: int, node: Coordinate, direction: CardinalDirection) -> Optional[Coordinate]:
    (x, y) = node
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


MAX_CONSECUTIVE_BLOCKS = 3


class Map(NamedTuple):
    width: int
    height: int
    rows_costs: tuple[tuple[int, ...], ...]

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Map':
        width = -1
        rows_costs: list[tuple[int, ...]] = []
        for (y, line) in enumerate(lines):
            # Ensure width is consistent across lines.
            if y == 0:
                width = len(line)
            elif len(line) != width:
                raise ValueError(f'Width of line {y + 1} differs from line 1 ({len(line)} ≠ {width})')
            rows_costs.append(tuple(int(char) for char in line))
        return Map(width, y + 1, tuple(rows_costs))

    def __str__(self) -> str:
        return '\n'.join(''.join(str(cost) for cost in row_costs) for row_costs in self.rows_costs)

    def find_minimal_heat_loss_path(self, start: Coordinate, goal: Coordinate) -> 'Path':
        open_set: list[Path] = []

        def add_to_open_set(path: Path):
            heappush(open_set, path)

        def heuristic_cost(node: Coordinate):
            return manhattan_distance(node, goal)

        def is_valid_path(path: Path) -> bool:
            return all(len(tuple(consecutive_directions)) <= MAX_CONSECUTIVE_BLOCKS
                       for (_, consecutive_directions)
                       in groupby(path.directions))

        def enumerate_neighbouring_paths(path: Path) -> Iterator[Path]:
            restricted_directions: set[CardinalDirection] = set()
            if path.directions:
                # We can't go backwards.
                restricted_directions.add(path.directions[-1].reverse)
                last_n_directions = path.directions[-MAX_CONSECUTIVE_BLOCKS:]
                if len(last_n_directions) == MAX_CONSECUTIVE_BLOCKS and len(set(last_n_directions)) == 1:
                    # We can't go in the same direction anymore.
                    restricted_directions.add(path.directions[-1])
            for direction in CardinalDirection:
                if direction in restricted_directions:
                    continue
                next_node = translate(self.width, self.height, path.end, direction)
                if not next_node:
                    continue
                next_directions = path.directions + (direction,)
                next_cost = path.cost + self.rows_costs[next_node.y][next_node.x]
                next_heuristic_cost = heuristic_cost(next_node)
                yield Path(path.start, next_node, next_directions, next_cost, next_heuristic_cost)

        add_to_open_set(Path(start, start, (), 0, heuristic_cost(start)))
        while open_set:
            current_path = heappop(open_set)
            if current_path.end == goal:
                assert is_valid_path(current_path)
                return current_path
            for neighbouring_path in enumerate_neighbouring_paths(current_path):
                add_to_open_set(neighbouring_path)

        raise ValueError(f'Cannot reach {goal!r} from {start!r}')


########################################################################################################################
# Part 1
########################################################################################################################

def calculate_minimal_heat_loss(lines: Iterable[str]) -> int:
    """
    >>> calculate_minimal_heat_loss([
    ...     '2413432311323',
    ...     '3215453535623',
    ...     '3255245654254',
    ...     '3446585845452',
    ...     '4546657867536',
    ...     '1438598798454',
    ...     '4457876987766',
    ...     '3637877979653',
    ...     '4654967986887',
    ...     '4564679986453',
    ...     '1224686865563',
    ...     '2546548887735',
    ...     '4322674655533',
    ... ])
    102
    """
    map_ = Map.from_lines(lines)
    best_path = map_.find_minimal_heat_loss_path(Coordinate(0, 0), Coordinate(map_.width - 1, map_.height - 1))
    return best_path.cost


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
        print(calculate_minimal_heat_loss(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
