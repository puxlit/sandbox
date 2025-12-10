#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable, Iterator
from heapq import heappop, heappush
import re
from typing import Callable, NamedTuple, TypeVar


########################################################################################################################
# A*
########################################################################################################################

T = TypeVar('T')


def calculate_optimal_cost(start: T, goal: T, enumerate_neighbouring_nodes: Callable[[T], Iterator[tuple[T, int]]], heuristic_cost: Callable[[T, T], int]) -> int:
    open_set: set[T] = set()
    open_heapq: list[tuple[int, T]] = []
    g_scores: dict[T, int] = {}
    f_scores: dict[T, int] = {}

    def add_to_open_set(next_node: T, g_score: int) -> None:
        g_scores[next_node] = g_score
        f_score = g_score + heuristic_cost(next_node, goal)
        f_scores[next_node] = f_score
        if next_node not in open_set:
            open_set.add(next_node)
            heappush(open_heapq, (f_score, next_node))

    def remove_from_open_set() -> T:
        (_, node) = heappop(open_heapq)
        open_set.remove(node)
        return node

    add_to_open_set(start, 0)
    while open_set:
        node = remove_from_open_set()
        if node == goal:
            return g_scores[node]
        for (next_node, edge_cost) in enumerate_neighbouring_nodes(node):
            tentative_g_score = g_scores[node] + edge_cost
            if (next_node not in g_scores) or (tentative_g_score < g_scores[next_node]):
                add_to_open_set(next_node, tentative_g_score)

    raise ValueError(f'Cannot reach {goal!r} from {start!r}')


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


def bit_positions_to_bools(width: int, bit_positions: Iterable[int]) -> tuple[bool, ...]:
    assert width > 0
    bools = [False] * width
    for bit_position in bit_positions:
        assert 0 <= bit_position < width
        bools[bit_position] = True
    return tuple(bools)


MACHINE_PATTERN = re.compile(r'^\[([#.]+)\] \((\d+(?:,\d+)*(?:\) \(\d+(?:,\d+)*)*)\) \{(\d+(?:,\d+)*)\}$')
INDICATOR_LIGHT_OFF = '.'
INDICATOR_LIGHT_ON = '#'
BUTTON_DELIMITER = ') ('
BUTTON_LIGHT_DELIMITER = ','
JOLTAGE_REQUIREMENT_DELIMITER = ','


class Machine(NamedTuple):
    indicator_lights: int
    buttons: tuple[tuple[int, tuple[bool, ...]], ...]
    joltage_requirements: tuple[int, ...]

    @classmethod
    def from_line(cls, line: str) -> 'Machine':
        """
        >>> Machine.from_line('[.##.] (3) (1,3) (2) (2,3) (0,2) (0,1) {3,5,4,7}')
        Machine(indicator_lights=6, buttons=((1, (False, False, False, True)), (5, (False, True, False, True)), (2, (False, False, True, False)), (3, (False, False, True, True)), (10, (True, False, True, False)), (12, (True, True, False, False))), joltage_requirements=(3, 5, 4, 7))
        >>> Machine.from_line('[...#.] (0,2,3,4) (2,3) (0,4) (0,1,2) (1,2,3,4) {7,5,12,7,2}')
        Machine(indicator_lights=2, buttons=((23, (True, False, True, True, True)), (6, (False, False, True, True, False)), (17, (True, False, False, False, True)), (28, (True, True, True, False, False)), (15, (False, True, True, True, True))), joltage_requirements=(7, 5, 12, 7, 2))
        >>> Machine.from_line('[.###.#] (0,1,2,3,4) (0,3,4) (0,1,2,4,5) (1,2) {10,11,11,5,10,5}')
        Machine(indicator_lights=29, buttons=((62, (True, True, True, True, True, False)), (38, (True, False, False, True, True, False)), (59, (True, True, True, False, True, True)), (24, (False, True, True, False, False, False))), joltage_requirements=(10, 11, 11, 5, 10, 5))
        """
        assert (match := MACHINE_PATTERN.match(line)) is not None

        (raw_indicator_light_diagram, raw_button_wiring_schematics, raw_joltage_requirements) = match.groups()

        num_indicator_lights = len(raw_indicator_light_diagram)
        all_indicator_lights = (2 ** num_indicator_lights) - 1
        indicator_lights = bools_to_bitmask({
            INDICATOR_LIGHT_OFF: False,
            INDICATOR_LIGHT_ON: True,
        }[char] for char in raw_indicator_light_diagram)

        button_bit_positions = tuple(
            tuple(int(raw_number) for raw_number in button.split(BUTTON_LIGHT_DELIMITER))
            for button in raw_button_wiring_schematics.split(BUTTON_DELIMITER)
        )
        assert all(
            (0 <= bit_position < num_indicator_lights)
            for button in button_bit_positions
            for bit_position in button
        )
        buttons = tuple((
            bit_positions_to_bitmask((num_indicator_lights - bit_position - 1) for bit_position in button),
            bit_positions_to_bools(num_indicator_lights, button),
        ) for button in button_bit_positions)
        assert all(button <= all_indicator_lights for (button, _) in buttons)

        joltage_requirements = tuple(int(raw_number) for raw_number in raw_joltage_requirements.split(JOLTAGE_REQUIREMENT_DELIMITER))
        assert len(joltage_requirements) == num_indicator_lights

        return Machine(indicator_lights, buttons, joltage_requirements)

    def count_fewest_button_presses_to_start(self) -> int:
        """
        >>> Machine.from_line('[.##.] (3) (1,3) (2) (2,3) (0,2) (0,1) {3,5,4,7}').count_fewest_button_presses_to_start()
        2
        >>> Machine.from_line('[...#.] (0,2,3,4) (2,3) (0,4) (0,1,2) (1,2,3,4) {7,5,12,7,2}').count_fewest_button_presses_to_start()
        3
        >>> Machine.from_line('[.###.#] (0,1,2,3,4) (0,3,4) (0,1,2,4,5) (1,2) {10,11,11,5,10,5}').count_fewest_button_presses_to_start()
        2
        """
        def enumerate_neighbouring_nodes(node: int) -> Iterator[tuple[int, int]]:
            for (button, _) in self.buttons:
                next_node = node ^ button
                yield (next_node, 1)

        def heuristic_cost(from_node: int, to_node: int) -> int:
            return 0

        return calculate_optimal_cost(0, self.indicator_lights, enumerate_neighbouring_nodes, heuristic_cost)

    def count_fewest_button_presses_to_configure(self) -> int:
        """
        >>> Machine.from_line('[.##.] (3) (1,3) (2) (2,3) (0,2) (0,1) {3,5,4,7}').count_fewest_button_presses_to_configure()
        10
        >>> Machine.from_line('[...#.] (0,2,3,4) (2,3) (0,4) (0,1,2) (1,2,3,4) {7,5,12,7,2}').count_fewest_button_presses_to_configure()
        12
        >>> Machine.from_line('[.###.#] (0,1,2,3,4) (0,3,4) (0,1,2,4,5) (1,2) {10,11,11,5,10,5}').count_fewest_button_presses_to_configure()
        11
        """
        start = (0,) * len(self.joltage_requirements)

        def enumerate_neighbouring_nodes(node: tuple[int, ...]) -> Iterator[tuple[tuple[int, ...], int]]:
            assert len(node) == len(self.joltage_requirements)
            for (_, button) in self.buttons:
                next_node = node
                edge_cost = 0
                while True:
                    next_node = tuple((a + b) for (a, b) in zip(next_node, button))
                    edge_cost += 1
                    if not all((a <= b) for (a, b) in zip(next_node, self.joltage_requirements)):
                        break
                    yield (next_node, edge_cost)

        def heuristic_cost(from_node: tuple[int, ...], to_node: tuple[int, ...]) -> int:
            assert len(from_node) == len(to_node)
            return max(abs(a - b) for (a, b) in zip(from_node, to_node))

        return calculate_optimal_cost(start, self.joltage_requirements, enumerate_neighbouring_nodes, heuristic_cost)


########################################################################################################################
# Part 1
########################################################################################################################

def count_fewest_button_presses_to_start_machines(lines: Iterable[str]) -> int:
    """
    >>> count_fewest_button_presses_to_start_machines([
    ...     '[.##.] (3) (1,3) (2) (2,3) (0,2) (0,1) {3,5,4,7}',
    ...     '[...#.] (0,2,3,4) (2,3) (0,4) (0,1,2) (1,2,3,4) {7,5,12,7,2}',
    ...     '[.###.#] (0,1,2,3,4) (0,3,4) (0,1,2,4,5) (1,2) {10,11,11,5,10,5}',
    ... ])
    7
    """
    return sum(Machine.from_line(line).count_fewest_button_presses_to_start() for line in lines)


########################################################################################################################
# Part 2
########################################################################################################################

def count_fewest_button_presses_to_configure_machines(lines: Iterable[str]) -> int:
    """
    >>> count_fewest_button_presses_to_configure_machines([
    ...     '[.##.] (3) (1,3) (2) (2,3) (0,2) (0,1) {3,5,4,7}',
    ...     '[...#.] (0,2,3,4) (2,3) (0,4) (0,1,2) (1,2,3,4) {7,5,12,7,2}',
    ...     '[.###.#] (0,1,2,3,4) (0,3,4) (0,1,2,4,5) (1,2) {10,11,11,5,10,5}',
    ... ])
    33
    """
    return sum(Machine.from_line(line).count_fewest_button_presses_to_configure() for line in lines)


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
        print(count_fewest_button_presses_to_start_machines(lines))
    elif args.part == 2:
        print(count_fewest_button_presses_to_configure_machines(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
