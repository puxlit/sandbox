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


class Node(NamedTuple):
    coord: Coordinate
    restricted_direction: Optional[CardinalDirection]


@dataclass(order=True, frozen=True)
class NodeWithCost:
    f_score: int
    node: Node = field(hash=True, compare=False)


class Path(NamedTuple):
    start: Coordinate
    goal: Coordinate
    directions: tuple[CardinalDirection, ...]
    cost: int


def manhattan_distance(a: Coordinate, b: Coordinate) -> int:
    return abs(a.x - b.x) + abs(a.y - b.y)


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

    def find_minimal_heat_loss_path(self, start: Coordinate, goal: Coordinate, min_moves: int, max_moves: int) -> 'Path':
        assert 1 <= min_moves <= max_moves

        open_set: set[Node] = set()
        open_heapq: list[NodeWithCost] = []
        came_from: dict[Node, Node] = {}
        g_scores: dict[Node, int] = {}
        f_scores: dict[Node, int] = {}

        def add_to_open_set(next_node: Node, g_score: int):
            g_scores[next_node] = g_score
            f_score = g_score + heuristic_cost(next_node.coord)
            f_scores[next_node] = f_score
            if next_node not in open_set:
                open_set.add(next_node)
                heappush(open_heapq, NodeWithCost(f_score, next_node))

        def remove_from_open_set() -> Node:
            node_with_cost = heappop(open_heapq)
            open_set.remove(node_with_cost.node)
            return node_with_cost.node

        def heuristic_cost(coord: Coordinate):
            return manhattan_distance(coord, goal)

        def reconstruct_path(node: Node) -> Path:
            assert node.coord == goal
            assert node.restricted_direction
            directions: tuple[CardinalDirection, ...] = ()
            cost = f_scores[node]
            while node in came_from:
                prev_node = came_from[node]
                directions = ((node.restricted_direction,) * manhattan_distance(prev_node.coord, node.coord)) + directions
                node = prev_node
                if not node.restricted_direction:
                    assert node.coord == start
                    break
            return Path(start, goal, directions, cost)

        def is_valid_path(path: Path) -> bool:
            return all(min_moves <= len(tuple(consecutive_directions)) <= max_moves
                       for (_, consecutive_directions)
                       in groupby(path.directions))

        def enumerate_neighbouring_nodes(node: Node) -> Iterator[tuple[Node, int]]:
            (coord, restricted_direction) = node
            # For simplicity, when enumerating neighbouring nodes, we assume we've gotten to this node by travelling
            # `max_moves` already. Also, we enforce not being able to traverse backwards.
            restricted_directions = {restricted_direction, restricted_direction.reverse} if restricted_direction else set()
            for next_direction in CardinalDirection:
                if next_direction in restricted_directions:
                    continue
                next_coord: Optional[Coordinate] = coord
                h_score = 0
                for i in range(max_moves):
                    assert next_coord
                    next_coord = translate(self.width, self.height, next_coord, next_direction)
                    if not next_coord:
                        # We've hit the map extent.
                        break
                    h_score += self.rows_costs[next_coord.y][next_coord.x]
                    if i >= min_moves - 1:
                        yield (Node(next_coord, next_direction), h_score)

        add_to_open_set(Node(start, None), 0)
        while open_set:
            node = remove_from_open_set()
            if node.coord == goal:
                best_path = reconstruct_path(node)
                assert is_valid_path(best_path)
                return best_path
            for (next_node, h_score) in enumerate_neighbouring_nodes(node):
                tentative_g_score = g_scores[node] + h_score
                if (next_node not in g_scores) or (tentative_g_score < g_scores[next_node]):
                    came_from[next_node] = node
                    add_to_open_set(next_node, tentative_g_score)

        raise ValueError(f'Cannot reach {goal!r} from {start!r}')


########################################################################################################################
# Part 1
########################################################################################################################

def calculate_minimal_crucible_heat_loss(lines: Iterable[str]) -> int:
    """
    >>> calculate_minimal_crucible_heat_loss([
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
    best_path = map_.find_minimal_heat_loss_path(Coordinate(0, 0), Coordinate(map_.width - 1, map_.height - 1), 1, 3)
    return best_path.cost


########################################################################################################################
# Part 2
########################################################################################################################

def calculate_minimal_ultra_crucible_heat_loss(lines: Iterable[str]) -> int:
    """
    >>> calculate_minimal_ultra_crucible_heat_loss([
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
    94
    >>> calculate_minimal_ultra_crucible_heat_loss([
    ...     '111111111111',
    ...     '999999999991',
    ...     '999999999991',
    ...     '999999999991',
    ...     '999999999991',
    ... ])
    71
    """
    map_ = Map.from_lines(lines)
    best_path = map_.find_minimal_heat_loss_path(Coordinate(0, 0), Coordinate(map_.width - 1, map_.height - 1), 4, 10)
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
        print(calculate_minimal_crucible_heat_loss(lines))
    elif args.part == 2:
        print(calculate_minimal_ultra_crucible_heat_loss(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
