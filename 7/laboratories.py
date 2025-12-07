#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable
from functools import cache, reduce


########################################################################################################################
# Tachyon manifold
########################################################################################################################

EMPTY_SPACE = '.'
BEAM_MANIFOLD_ENTRANCE = 'S'
BEAM_SPLITTER = '^'


def parse_diagram(lines: Iterable[str]) -> tuple[tuple[bool, ...], tuple[tuple[bool, ...], ...]]:
    lines_iter = iter(lines)

    beam_positions = tuple({
        EMPTY_SPACE: False,
        BEAM_MANIFOLD_ENTRANCE: True,
    }[char] for char in next(lines_iter))
    assert (width := len(beam_positions)) > 1
    assert sum(has_beam for has_beam in beam_positions) == 1

    all_splitter_positions: list[tuple[bool, ...]] = []
    for line in lines_iter:
        splitter_positions = tuple({
            EMPTY_SPACE: False,
            BEAM_SPLITTER: True,
        }[char] for char in line)
        assert len(splitter_positions) == width
        all_splitter_positions.append(splitter_positions)

    return (beam_positions, tuple(all_splitter_positions))


@cache
def simulate_step(beam_positions: tuple[bool, ...], splitter_positions: tuple[bool, ...]) -> tuple[tuple[bool, ...], int]:
    assert len(splitter_positions) == (width := len(beam_positions))
    next_beam_positions: list[bool] = [False] * width
    new_beam_splits = 0
    for i in range(width):
        if not beam_positions[i]:
            # There's no incoming beam.
            continue
        if not splitter_positions[i]:
            # The incoming beam freely travels through empty space.
            next_beam_positions[i] = True
            continue
        # We're splittin' the beam.
        new_beam_splits += 1
        # Maybe split to the left.
        if (i > 0) and not next_beam_positions[i - 1]:
            next_beam_positions[i - 1] = True
        # Maybe split to the right.
        if (i < width - 1) and not next_beam_positions[i + 1]:
            next_beam_positions[i + 1] = True
    return (tuple(next_beam_positions), new_beam_splits)


def simulate_step_with_stats(beam_positions_and_stats: tuple[tuple[bool, ...], int], splitter_positions: tuple[bool, ...]) -> tuple[tuple[bool, ...], int]:
    (beam_positions, num_beam_splits) = beam_positions_and_stats
    (next_beam_positions, new_beam_splits) = simulate_step(beam_positions, splitter_positions)
    return (next_beam_positions, num_beam_splits + new_beam_splits)


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
    (initial_beam_positions, all_splitter_positions) = parse_diagram(lines)
    (final_beam_positions, num_beam_splits) = reduce(simulate_step_with_stats, all_splitter_positions, (initial_beam_positions, 0))
    return num_beam_splits


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
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
