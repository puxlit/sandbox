#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable
from functools import reduce


########################################################################################################################
# Tachyon manifold
########################################################################################################################

EMPTY_SPACE = '.'
BEAM_MANIFOLD_ENTRANCE = 'S'
BEAM_SPLITTER = '^'


def parse_diagram(lines: Iterable[str]) -> tuple[tuple[int, ...], tuple[tuple[bool, ...], ...]]:
    lines_iter = iter(lines)

    beam_timelines = tuple({
        EMPTY_SPACE: 0,
        BEAM_MANIFOLD_ENTRANCE: 1,
    }[char] for char in next(lines_iter))
    assert (width := len(beam_timelines)) > 1
    assert sum(has_beam for has_beam in beam_timelines) == 1

    all_splitter_positions: list[tuple[bool, ...]] = []
    for line in lines_iter:
        splitter_positions = tuple({
            EMPTY_SPACE: False,
            BEAM_SPLITTER: True,
        }[char] for char in line)
        assert len(splitter_positions) == width
        all_splitter_positions.append(splitter_positions)

    return (beam_timelines, tuple(all_splitter_positions))


def simulate_step(beam_timelines: tuple[int, ...], splitter_positions: tuple[bool, ...]) -> tuple[tuple[int, ...], int]:
    assert len(splitter_positions) == (width := len(beam_timelines))
    next_beam_timelines = list(beam_timelines)
    new_beam_splits = 0
    for i in range(width):
        if not beam_timelines[i]:
            # There's no incoming beam.
            continue
        if not splitter_positions[i]:
            # The incoming beam freely travels through empty space.
            continue
        # We're splittin' the beam.
        next_beam_timelines[i] = 0
        new_beam_splits += 1
        # Maybe split to the left.
        if i > 0:
            next_beam_timelines[i - 1] += beam_timelines[i]
        # Maybe split to the right.
        if i < (width - 1):
            next_beam_timelines[i + 1] += beam_timelines[i]
    return (tuple(next_beam_timelines), new_beam_splits)


def simulate_step_with_stats(beam_timelines_and_stats: tuple[tuple[int, ...], int], splitter_positions: tuple[bool, ...]) -> tuple[tuple[int, ...], int]:
    (beam_timelines, num_beam_splits) = beam_timelines_and_stats
    (next_beam_timelines, new_beam_splits) = simulate_step(beam_timelines, splitter_positions)
    return (next_beam_timelines, num_beam_splits + new_beam_splits)


########################################################################################################################
# Part 1
########################################################################################################################

def count_beam_splits(lines: Iterable[str]) -> int:
    """
    >>> count_beam_splits([
    ...     '.......S.......',
    ...     '...............',
    ...     '.......^.......',
    ...     '...............',
    ...     '......^.^......',
    ...     '...............',
    ...     '.....^.^.^.....',
    ...     '...............',
    ...     '....^.^...^....',
    ...     '...............',
    ...     '...^.^...^.^...',
    ...     '...............',
    ...     '..^...^.....^..',
    ...     '...............',
    ...     '.^.^.^.^.^...^.',
    ...     '...............',
    ... ])
    21
    """
    (initial_beam_timelines, all_splitter_positions) = parse_diagram(lines)
    (_, num_beam_splits) = reduce(simulate_step_with_stats, all_splitter_positions, (initial_beam_timelines, 0))
    return num_beam_splits


########################################################################################################################
# Part 2
########################################################################################################################

def count_timelines(lines: Iterable[str]) -> int:
    """
    >>> count_timelines([
    ...     '.......S.......',
    ...     '...............',
    ...     '.......^.......',
    ...     '...............',
    ...     '......^.^......',
    ...     '...............',
    ...     '.....^.^.^.....',
    ...     '...............',
    ...     '....^.^...^....',
    ...     '...............',
    ...     '...^.^...^.^...',
    ...     '...............',
    ...     '..^...^.....^..',
    ...     '...............',
    ...     '.^.^.^.^.^...^.',
    ...     '...............',
    ... ])
    40
    """
    (initial_beam_timelines, all_splitter_positions) = parse_diagram(lines)
    (final_beam_timelines, _) = reduce(simulate_step_with_stats, all_splitter_positions, (initial_beam_timelines, 0))
    return sum(final_beam_timelines)


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
        print(count_beam_splits(lines))
    elif args.part == 2:
        print(count_timelines(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
