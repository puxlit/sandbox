#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from heapq import heappop, heappush
from itertools import combinations
from math import prod, sqrt
from typing import NamedTuple


########################################################################################################################
# Circuits
########################################################################################################################

COORDINATE_DELIMITER = ','


class JunctionBox(NamedTuple):
    x: int
    y: int
    z: int

    @classmethod
    def from_line(cls, line: str) -> 'JunctionBox':
        (raw_x, raw_y, raw_z) = line.split(COORDINATE_DELIMITER)
        return JunctionBox(int(raw_x), int(raw_y), int(raw_z))


@dataclass
class Circuits:
    junction_box_circuits: dict[JunctionBox, int]
    circuit_junction_boxes: dict[int, set[JunctionBox]]

    @classmethod
    def from_junction_boxes(cls, junction_boxes: Iterable[JunctionBox]) -> 'Circuits':
        junction_box_circuits: dict[JunctionBox, int] = {}
        circuit_junction_boxes: dict[int, set[JunctionBox]] = {}
        next_circuit_id = 0
        for junction_box in junction_boxes:
            assert junction_box not in junction_box_circuits
            junction_box_circuits[junction_box] = next_circuit_id
            circuit_junction_boxes[next_circuit_id] = {junction_box}
            next_circuit_id += 1
        return Circuits(junction_box_circuits, circuit_junction_boxes)

    def maybe_connect_pair(self, a: JunctionBox, b: JunctionBox) -> bool:
        circuit_id_a = self.junction_box_circuits[a]
        circuit_id_b = self.junction_box_circuits[b]
        if circuit_id_a == circuit_id_b:
            return False
        # Arbitrarily subsume circuit B into circuit A.
        for bb in self.circuit_junction_boxes[circuit_id_b]:
            self.junction_box_circuits[bb] = circuit_id_a
        self.circuit_junction_boxes[circuit_id_a].update(self.circuit_junction_boxes[circuit_id_b])
        del self.circuit_junction_boxes[circuit_id_b]
        return True


def calculate_euclidean_distance(a: JunctionBox, b: JunctionBox) -> float:
    return sqrt(pow(a.x - b.x, 2) + pow(a.y - b.y, 2) + pow(a.z - b.z, 2))


def pairs_by_distance(junction_boxes: Iterable[JunctionBox]) -> Iterator[tuple[JunctionBox, JunctionBox]]:
    # A complete graph of n vertices has n(n-1)÷2 edges. So 1,000 vertices would have 499,500 edges.
    pairs: list[tuple[float, tuple[JunctionBox, JunctionBox]]] = []
    for (a, b) in combinations(junction_boxes, 2):
        distance = calculate_euclidean_distance(a, b)
        heappush(pairs, (distance, (a, b)))
    while pairs:
        (_, pair) = heappop(pairs)
        yield pair


def parse_junction_boxes(lines: Iterable[str]) -> Iterator[JunctionBox]:
    for line in lines:
        yield JunctionBox.from_line(line)


########################################################################################################################
# Part 1
########################################################################################################################

def multiply_three_largest_circuit_sizes_after_n_connections(lines: Iterable[str], num_connections: int) -> int:
    """
    >>> multiply_three_largest_circuit_sizes_after_n_connections([
    ...     '162,817,812',
    ...     '57,618,57',
    ...     '906,360,560',
    ...     '592,479,940',
    ...     '352,342,300',
    ...     '466,668,158',
    ...     '542,29,236',
    ...     '431,825,988',
    ...     '739,650,466',
    ...     '52,470,668',
    ...     '216,146,977',
    ...     '819,987,18',
    ...     '117,168,530',
    ...     '805,96,715',
    ...     '346,949,466',
    ...     '970,615,88',
    ...     '941,993,340',
    ...     '862,61,35',
    ...     '984,92,344',
    ...     '425,690,689',
    ... ], 10)
    40
    """
    assert num_connections > 0

    junction_boxes = tuple(parse_junction_boxes(lines))
    circuits = Circuits.from_junction_boxes(junction_boxes)

    pairs = pairs_by_distance(junction_boxes)
    for _ in range(num_connections):
        # Apparently, we count pairs that don't actually form a connection.
        circuits.maybe_connect_pair(*next(pairs))

    assert len(circuits.circuit_junction_boxes) >= 3
    return prod(sorted(map(len, circuits.circuit_junction_boxes.values()), reverse=True)[:3])


def multiply_three_largest_circuit_sizes_after_one_thousand_connections(lines: Iterable[str]) -> int:
    return multiply_three_largest_circuit_sizes_after_n_connections(lines, 1000)


########################################################################################################################
# Part 2
########################################################################################################################

def multiply_x_coordinates_of_last_connection(lines: Iterable[str]) -> int:
    """
    >>> multiply_x_coordinates_of_last_connection([
    ...     '162,817,812',
    ...     '57,618,57',
    ...     '906,360,560',
    ...     '592,479,940',
    ...     '352,342,300',
    ...     '466,668,158',
    ...     '542,29,236',
    ...     '431,825,988',
    ...     '739,650,466',
    ...     '52,470,668',
    ...     '216,146,977',
    ...     '819,987,18',
    ...     '117,168,530',
    ...     '805,96,715',
    ...     '346,949,466',
    ...     '970,615,88',
    ...     '941,993,340',
    ...     '862,61,35',
    ...     '984,92,344',
    ...     '425,690,689',
    ... ])
    25272
    """
    junction_boxes = tuple(parse_junction_boxes(lines))
    circuits = Circuits.from_junction_boxes(junction_boxes)

    for (a, b) in pairs_by_distance(junction_boxes):
        circuits.maybe_connect_pair(a, b)
        if len(circuits.circuit_junction_boxes) == 1:
            break
    assert len(circuits.circuit_junction_boxes) == 1

    return a.x * b.x


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
        print(multiply_three_largest_circuit_sizes_after_one_thousand_connections(lines))
    elif args.part == 2:
        print(multiply_x_coordinates_of_last_connection(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
