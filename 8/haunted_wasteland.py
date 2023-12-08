#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterator
from enum import Enum
from itertools import cycle
import re


########################################################################################################################
# Part 1
########################################################################################################################

INSTRUCTIONS_PATTERN = re.compile(r'^[LR]+$')


class Instruction(Enum):
    LEFT = 'L'
    RIGHT = 'R'

    @classmethod
    def from_line(cls, line: str) -> tuple['Instruction', ...]:
        match = INSTRUCTIONS_PATTERN.fullmatch(line)
        if not match:
            raise ValueError(f'Instructions line {line!r} does not match '
                             f'expected pattern /{INSTRUCTIONS_PATTERN.pattern}/')
        return tuple(Instruction(instruction) for instruction in match.group(0))


NODE_PATTERN = re.compile(r'^([A-Z]{3}) = \(([A-Z]{3}), ([A-Z]{3})\)$')
SOURCE_NODE = 'AAA'
GOAL_NODE = 'ZZZ'


def parse_network(lines: Iterator[str]) -> dict[str, tuple[str, str]]:
    network: dict[str, tuple[str, str]] = {}
    undefined_nodes: set[str] = set()
    for line in lines:
        match = NODE_PATTERN.fullmatch(line)
        if not match:
            raise ValueError(f'Node line {line!r} does not match '
                             f'expected pattern /{NODE_PATTERN.pattern}/')
        (node, left_node, right_node) = match.groups()
        if node in network:
            raise ValueError(f'Encountered duplicate node definition line {line!r}')
        network[node] = (left_node, right_node)
        if node in undefined_nodes:
            undefined_nodes.remove(node)
        if left_node not in network and left_node not in undefined_nodes:
            undefined_nodes.add(left_node)
        if right_node not in network and right_node not in undefined_nodes:
            undefined_nodes.add(right_node)
    if SOURCE_NODE not in network:
        raise ValueError(f'Network is missing source node {SOURCE_NODE!r}')
    if GOAL_NODE not in network:
        raise ValueError(f'Network is missing goal node {GOAL_NODE!r}')
    if undefined_nodes:
        raise ValueError(f'Network is missing node definition(s): {undefined_nodes!r}')
    return network


def count_naive_steps(lines: Iterator[str]) -> int:
    """
    >>> count_naive_steps(iter([
    ...     'RL',
    ...     '',
    ...     'AAA = (BBB, CCC)',
    ...     'BBB = (DDD, EEE)',
    ...     'CCC = (ZZZ, GGG)',
    ...     'DDD = (DDD, DDD)',
    ...     'EEE = (EEE, EEE)',
    ...     'GGG = (GGG, GGG)',
    ...     'ZZZ = (ZZZ, ZZZ)',
    ... ]))
    2
    >>> count_naive_steps(iter([
    ...     'LLR',
    ...     '',
    ...     'AAA = (BBB, BBB)',
    ...     'BBB = (AAA, ZZZ)',
    ...     'ZZZ = (ZZZ, ZZZ)',
    ... ]))
    6
    """
    instructions = Instruction.from_line(next(lines))
    if next(lines):
        raise ValueError('Expected blank line')
    network = parse_network(lines)

    node = SOURCE_NODE
    steps = 0
    # TODO: Be fancy and detect cycles.
    for instruction in cycle(instructions):
        node = (
            network[node][0] if instruction == Instruction.LEFT else
            network[node][1] if instruction == Instruction.RIGHT else
            'unreachable'  # TODO: Upgrade to Python 3.10 so I can finally use structural pattern matching. 😭
        )
        steps += 1
        if node == GOAL_NODE:
            break
    return steps


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
        print(count_naive_steps(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
