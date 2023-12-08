#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterator
from dataclasses import dataclass
from enum import Enum
from itertools import cycle, islice, repeat
from math import lcm
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


NODE_PATTERN = re.compile(r'^([0-9A-Z]{3}) = \(([0-9A-Z]{3}), ([0-9A-Z]{3})\)$')
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
    if undefined_nodes:
        raise ValueError(f'Network is missing node definition(s): {undefined_nodes!r}')
    return network


def count_corporeal_steps(lines: Iterator[str]) -> int:
    """
    >>> count_corporeal_steps(iter([
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
    >>> count_corporeal_steps(iter([
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
    if SOURCE_NODE not in network:
        raise ValueError(f'Network is missing source node {SOURCE_NODE!r}')
    if GOAL_NODE not in network:
        raise ValueError(f'Network is missing goal node {GOAL_NODE!r}')

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
# Part 2
########################################################################################################################

@dataclass
class Path:
    start_node: str
    node_steps: dict[str, list[int]]
    cycle_start_step: int
    cycle_length: int
    cycle_goal_nodes_steps: dict[str, list[int]]


def count_phantom_steps(lines: Iterator[str]) -> int:
    """
    >>> count_phantom_steps(iter([
    ...     'LR',
    ...     '',
    ...     '11A = (11B, XXX)',
    ...     '11B = (XXX, 11Z)',
    ...     '11Z = (11B, XXX)',
    ...     '22A = (22B, XXX)',
    ...     '22B = (22C, 22C)',
    ...     '22C = (22Z, 22Z)',
    ...     '22Z = (22B, 22B)',
    ...     'XXX = (XXX, XXX)',
    ... ]))
    6
    """
    instructions = Instruction.from_line(next(lines))
    if next(lines):
        raise ValueError('Expected blank line')
    network = parse_network(lines)

    paths: dict[str, Path] = {}
    for start_node in network.keys():
        if not start_node.endswith('A'):
            continue
        path = Path(start_node, {start_node: [0]}, -1, -1, {})
        paths[start_node] = path

        node = start_node
        steps = 0
        found_goal_node = False
        found_stable_cycle = False
        for instruction in cycle(instructions):
            if instruction == Instruction.LEFT:
                node = network[node][0]
            elif instruction == Instruction.RIGHT:
                node = network[node][1]
            else:
                raise ValueError(f'Unexpected instruction {instruction!r}')
            steps += 1

            if node.endswith('Z'):
                found_goal_node = True

            if node in path.node_steps and found_goal_node:
                # We might have a cycle! (This is only worth validating once we've found a goal node.)
                speculative_nodes_cache: list[str] = []  # First item would be resultant node of the _next_ step.
                for candidate_cycle_start_step in path.node_steps[node]:
                    candidate_cycle_length = steps - candidate_cycle_start_step
                    assert candidate_cycle_length >= 1
                    # Test whether this cycle is stable with future instructions.
                    lcm_ = lcm(candidate_cycle_length, len(instructions))
                    if lcm_ - candidate_cycle_length > 0:
                        if len(speculative_nodes_cache) >= lcm_ - candidate_cycle_length:
                            speculative_node = speculative_nodes_cache[lcm_ - candidate_cycle_length - 1]
                            assert speculative_node != ''
                        else:
                            if speculative_nodes_cache:
                                speculative_node = speculative_nodes_cache[-1]
                                assert speculative_node != ''
                            else:
                                # Cache is empty.
                                speculative_node = node
                            speculative_instructions = islice(cycle(instructions), steps + len(speculative_nodes_cache), candidate_cycle_start_step + lcm_)
                            i = len(speculative_nodes_cache)
                            speculative_nodes_cache.extend(repeat('', lcm_ - candidate_cycle_length - len(speculative_nodes_cache)))
                            for speculative_instruction in speculative_instructions:
                                if instruction == Instruction.LEFT:
                                    speculative_node = network[speculative_node][0]
                                elif instruction == Instruction.RIGHT:
                                    speculative_node = network[speculative_node][1]
                                else:
                                    raise ValueError(f'Unexpected instruction {instruction!r}')
                                speculative_nodes_cache[i] = speculative_node
                                i += 1
                        if speculative_node != node:
                            continue
                    # We've confirmed we've got a stable loop!
                    path.cycle_start_step = candidate_cycle_start_step
                    path.cycle_length = candidate_cycle_length
                    found_stable_cycle = True
                    break
            if found_stable_cycle:
                path.cycle_goal_nodes_steps = {
                    node: list(filter(lambda x: x >= 0, (step - candidate_cycle_start_step for step in steps)))
                    for (node, steps)
                    in path.node_steps.items()
                    if node.endswith('Z')
                }
                break
            path.node_steps.setdefault(node, []).append(steps)

    # I'd generalise this solution, but the puzzle didn't bother to give us multiple gnarly cycles/goal nodes.
    for path in paths.values():
        assert len(path.cycle_goal_nodes_steps) == 1
        assert len(path.cycle_goal_nodes_steps.values()) == 1
        assert path.cycle_length == path.cycle_start_step + next(iter(path.cycle_goal_nodes_steps.values()))[0]
    # In the simplified case, we have only one cycle. Within that cycle, there's only one goal node, which appears only
    # once.
    #
    # The number of steps it can take to reach the goal node from a start node can thus be expressed as follows.
    #
    # steps = cycle_start_step + (n * cycle_length) + cycle_goal_node_step (where n ≥ 0)
    #
    # We now want to find the lowest common number of steps across all start nodes. Because, in our simplified case,
    # cycle_length = cycle_start_step + cycle_goal_node_step, this is as simple as calculating the lowest common
    # multiple of all the cycle lengths.
    return lcm(*(path.cycle_length for path in paths.values()))


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
        print(count_corporeal_steps(lines))
    elif args.part == 2:
        print(count_phantom_steps(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
