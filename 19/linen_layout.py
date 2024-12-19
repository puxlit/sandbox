#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable, Iterator
from functools import cache


########################################################################################################################
# Onsen
########################################################################################################################

STRIPE_COLOURS = {
    'w',  # white
    'u',  # blue
    'b',  # black
    'r',  # red
    'g',  # green
}


def valid_colours(towel_pattern_or_design: str) -> bool:
    return (len(towel_pattern_or_design) > 0) and all((stripe_colour in STRIPE_COLOURS) for stripe_colour in towel_pattern_or_design)


def parse_available_towel_patterns(line: str) -> frozenset[str]:
    available_towel_patterns: set[str] = set()
    for available_towel_pattern in line.split(', '):
        assert valid_colours(available_towel_pattern)
        available_towel_patterns.add(available_towel_pattern)
    return frozenset(available_towel_patterns)


def parse_desired_designs(lines: Iterable[str]) -> Iterator[str]:
    for desired_design in lines:
        assert valid_colours(desired_design)
        yield desired_design


def parse_input(lines: Iterable[str]) -> tuple[frozenset[str], Iterator[str]]:
    lines_iter = iter(lines)
    available_towel_patterns = parse_available_towel_patterns(next(lines_iter))
    assert next(lines_iter) == ''
    desired_designs = parse_desired_designs(lines_iter)
    return (available_towel_patterns, desired_designs)


########################################################################################################################
# Part 1
########################################################################################################################

@cache
def is_design_possible(desired_design: str, available_towel_patterns: frozenset[str]) -> bool:
    r"""
    >>> available_towel_patterns = parse_available_towel_patterns('r, wr, b, g, bwu, rb, gb, br')
    >>> tuple(filter(lambda desired_design: is_design_possible(desired_design, available_towel_patterns), [
    ...     'brwrr',
    ...     'bggr',
    ...     'gbbr',
    ...     'rrbgbr',
    ...     'ubwu',
    ...     'bwurrg',
    ...     'brgr',
    ...     'bbrgwb',
    ... ]))
    ('brwrr', 'bggr', 'gbbr', 'rrbgbr', 'bwurrg', 'brgr')

    >>> with open('input.txt', mode='rt') as input_file:
    ...     lines = [line.rstrip('\n') for line in input_file]
    >>> available_towel_patterns = parse_available_towel_patterns(lines[0])
    >>> is_design_possible(lines[9], available_towel_patterns)  # catastrophic backtracking (without memoisation)
    False
    """
    if len(desired_design) == 0:
        return True
    for available_towel_pattern in available_towel_patterns:
        if desired_design.startswith(available_towel_pattern) and is_design_possible(desired_design[len(available_towel_pattern):], available_towel_patterns):
            return True
    return False


def count_possible_designs(lines: Iterable[str]) -> int:
    """
    >>> count_possible_designs([
    ...     'r, wr, b, g, bwu, rb, gb, br',
    ...     '',
    ...     'brwrr',
    ...     'bggr',
    ...     'gbbr',
    ...     'rrbgbr',
    ...     'ubwu',
    ...     'bwurrg',
    ...     'brgr',
    ...     'bbrgwb',
    ... ])
    6
    """
    (available_towel_patterns, desired_designs) = parse_input(lines)
    return sum(is_design_possible(desired_design, available_towel_patterns) for desired_design in desired_designs)


########################################################################################################################
# Part 2
########################################################################################################################

@cache
def count_design_arrangements(desired_design: str, available_towel_patterns: frozenset[str]) -> int:
    """
    >>> available_towel_patterns = parse_available_towel_patterns('r, wr, b, g, bwu, rb, gb, br')
    >>> tuple(map(lambda desired_design: count_design_arrangements(desired_design, available_towel_patterns), [
    ...     'brwrr',
    ...     'bggr',
    ...     'gbbr',
    ...     'rrbgbr',
    ...     'ubwu',
    ...     'bwurrg',
    ...     'brgr',
    ...     'bbrgwb',
    ... ]))
    (2, 1, 4, 6, 0, 1, 2, 0)
    """
    if len(desired_design) == 0:
        return 1
    num_design_arrangements = 0
    for available_towel_pattern in available_towel_patterns:
        if desired_design.startswith(available_towel_pattern):
            num_design_arrangements += count_design_arrangements(desired_design[len(available_towel_pattern):], available_towel_patterns)
    return num_design_arrangements


def count_all_design_arrangements(lines: Iterable[str]) -> int:
    """
    >>> count_all_design_arrangements([
    ...     'r, wr, b, g, bwu, rb, gb, br',
    ...     '',
    ...     'brwrr',
    ...     'bggr',
    ...     'gbbr',
    ...     'rrbgbr',
    ...     'ubwu',
    ...     'bwurrg',
    ...     'brgr',
    ...     'bbrgwb',
    ... ])
    16
    """
    (available_towel_patterns, desired_designs) = parse_input(lines)
    return sum(count_design_arrangements(desired_design, available_towel_patterns) for desired_design in desired_designs)


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
        print(count_possible_designs(lines))
    elif args.part == 2:
        print(count_all_design_arrangements(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
