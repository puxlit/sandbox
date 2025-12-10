#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable, Iterator
from heapq import heappop, heappush
import re
from typing import Callable, NamedTuple


########################################################################################################################
# Factory
########################################################################################################################

def bools_to_bitmask(bools: Iterable[bool]) -> int:
    bitmask = 0
    for bool_ in bools:
        bitmask = (bitmask << 1) | bool_
    return bitmask


def bit_positions_to_bitmask(bit_positions: Iterable[int]) -> int:
    bitmask = 0
    for bit_position in bit_positions:
        assert bit_position >= 0
        bitmask |= (1 << bit_position)
    return bitmask


MACHINE_PATTERN = re.compile(r'^\[([#.]+)\] \((\d+(?:,\d+)*(?:\) \(\d+(?:,\d+)*)*)\) \{(\d+(?:,\d+)*)\}$')
INDICATOR_LIGHT_OFF = '.'
INDICATOR_LIGHT_ON = '#'
BUTTON_DELIMITER = ') ('
BUTTON_LIGHT_DELIMITER = ','
JOLTAGE_REQUIREMENT_DELIMITER = ','


class Machine(NamedTuple):
    indicator_lights: int
    buttons: tuple[int, ...]
    joltage_requirements: tuple[int, ...]

    @classmethod
    def from_line(cls, line: str) -> 'Machine':
        """
        >>> Machine.from_line('[.##.] (3) (1,3) (2) (2,3) (0,2) (0,1) {3,5,4,7}')
        Machine(indicator_lights=6, buttons=(1, 5, 2, 3, 10, 12), joltage_requirements=(3, 5, 4, 7))
        >>> Machine.from_line('[...#.] (0,2,3,4) (2,3) (0,4) (0,1,2) (1,2,3,4) {7,5,12,7,2}')
        Machine(indicator_lights=2, buttons=(23, 6, 17, 28, 15), joltage_requirements=(7, 5, 12, 7, 2))
        >>> Machine.from_line('[.###.#] (0,1,2,3,4) (0,3,4) (0,1,2,4,5) (1,2) {10,11,11,5,10,5}')
        Machine(indicator_lights=29, buttons=(62, 38, 59, 24), joltage_requirements=(10, 11, 11, 5, 10, 5))
        """
        assert (match := MACHINE_PATTERN.match(line)) is not None

        (raw_indicator_light_diagram, raw_button_wiring_schematics, raw_joltage_requirements) = match.groups()

        num_indicator_lights = len(raw_indicator_light_diagram)
        all_indicator_lights = (2 ** num_indicator_lights) - 1
        indicator_lights = bools_to_bitmask({
            INDICATOR_LIGHT_OFF: False,
            INDICATOR_LIGHT_ON: True,
        }[char] for char in raw_indicator_light_diagram)

        buttons = tuple(
            bit_positions_to_bitmask((num_indicator_lights - int(raw_number) - 1) for raw_number in button.split(BUTTON_LIGHT_DELIMITER))
            for button in raw_button_wiring_schematics.split(BUTTON_DELIMITER)
        )
        assert all(button <= all_indicator_lights for button in buttons)

        joltage_requirements = tuple(int(raw_number) for raw_number in raw_joltage_requirements.split(JOLTAGE_REQUIREMENT_DELIMITER))
        assert len(joltage_requirements) == num_indicator_lights

        return Machine(indicator_lights, buttons, joltage_requirements)

    def calculate_optimal_cost(self, calculate_edge_cost: Callable[[int, int], int]) -> int:
        # There might be a clever way to solve this with linear algebra, but for now, a shortest-path algorithm will do.
        # As we don't have a good heuristic function, we don't need A*; Dijkstra's is sufficient.

        open_set: set[int] = set()
        open_heapq: list[tuple[int, int]] = []
        g_scores: dict[int, int] = {}

        def add_to_open_set(next_node: int, g_score: int) -> None:
            g_scores[next_node] = g_score
            if next_node not in open_set:
                open_set.add(next_node)
                heappush(open_heapq, (g_score, next_node))

        def remove_from_open_set() -> int:
            (_, node) = heappop(open_heapq)
            open_set.remove(node)
            return node

        def enumerate_neighbouring_nodes(node: int) -> Iterator[tuple[int, int]]:
            for button in self.buttons:
                next_node = node ^ button
                edge_cost = calculate_edge_cost(node, next_node)
                yield (next_node, edge_cost)

        start = 0
        goal = self.indicator_lights

        add_to_open_set(start, 0)
        while open_set:
            node = remove_from_open_set()
            if node == goal:
                return g_scores[node]
            for (next_node, edge_cost) in enumerate_neighbouring_nodes(node):
                next_g_score = g_scores[node] + edge_cost
                if (next_node not in g_scores) or (next_g_score < g_scores[next_node]):
                    add_to_open_set(next_node, next_g_score)

        raise ValueError(f'Cannot reach {goal!r} from {start!r}')

    def count_fewest_button_presses(self) -> int:
        """
        >>> Machine.from_line('[.##.] (3) (1,3) (2) (2,3) (0,2) (0,1) {3,5,4,7}').count_fewest_button_presses()
        2
        >>> Machine.from_line('[...#.] (0,2,3,4) (2,3) (0,4) (0,1,2) (1,2,3,4) {7,5,12,7,2}').count_fewest_button_presses()
        3
        >>> Machine.from_line('[.###.#] (0,1,2,3,4) (0,3,4) (0,1,2,4,5) (1,2) {10,11,11,5,10,5}').count_fewest_button_presses()
        2
        """
        return self.calculate_optimal_cost(lambda from_node, to_node: 1)


########################################################################################################################
# Part 1
########################################################################################################################

def count_fewest_button_presses(lines: Iterable[str]) -> int:
    """
    >>> count_fewest_button_presses([
    ...     '[.##.] (3) (1,3) (2) (2,3) (0,2) (0,1) {3,5,4,7}',
    ...     '[...#.] (0,2,3,4) (2,3) (0,4) (0,1,2) (1,2,3,4) {7,5,12,7,2}',
    ...     '[.###.#] (0,1,2,3,4) (0,3,4) (0,1,2,4,5) (1,2) {10,11,11,5,10,5}',
    ... ])
    7
    """
    return sum(Machine.from_line(line).count_fewest_button_presses() for line in lines)


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
        print(count_fewest_button_presses(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
