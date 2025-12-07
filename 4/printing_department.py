#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable
from dataclasses import dataclass


########################################################################################################################
# Diagram
########################################################################################################################

EMPTY_SPACE = '.'
PAPER_ROLL = '@'


@dataclass
class Diagram:
    width: int
    height: int
    tiles: list[int]
    indices: tuple[int, ...]
    kernel_offsets: tuple[int, int, int, int, int, int, int, int]

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Diagram':
        width = padded_width = -1
        tiles: list[int] = []
        for (y, line) in enumerate(lines):
            # Ensure width is consistent across lines.
            if y == 0:
                width = len(line)
                padded_width = width + 2
                # Introduce top row of padding to reduce operations within `mark_neighbourhood_paper_rolls`.
                tiles.extend([0] * padded_width)
            elif len(line) != width:
                raise ValueError(f'Width of line {y + 1} differs from line 1 ({len(line)} ≠ {width})')
            # Introduce left and right columns of padding to reduce operations within `mark_neighbourhood_paper_rolls`.
            tiles.extend([0, *({
                EMPTY_SPACE: 0,
                PAPER_ROLL: 1,
            }[char] for char in line), 0])
        # Introduce bottom row of padding to reduce operations within `mark_neighbourhood_paper_rolls`.
        tiles.extend([0] * padded_width)
        height = y + 1
        padded_height = height + 2
        assert len(tiles) == padded_width * padded_height

        indices = tuple(
            (padded_width * (y + 1)) + (x + 1)
            for y in range(height)
            for x in range(width)
        )
        assert len(indices) == width * height
        kernel_offsets = (
            -padded_width - 1,  # North-west
            -padded_width,      # North tile
            -padded_width + 1,  # North-east
            -1,                 # West
            1,                  # East
            padded_width - 1,   # South-west
            padded_width,       # South
            padded_width + 1,   # South-east
        )
        return Diagram(width, height, tiles, indices, kernel_offsets)

    def mark_neighbourhood_paper_rolls(self) -> None:
        # Reduce attribute lookups.
        tiles = self.tiles
        kernel_offsets = self.kernel_offsets
        for i in self.indices:
            if tiles[i]:
                adjacent_paper_rolls = 0
                for kernel_i in kernel_offsets:
                    if tiles[i + kernel_i]:
                        adjacent_paper_rolls += 1
                tiles[i] += adjacent_paper_rolls

    def count_accessible_paper_rolls(self, max_adjacent_paper_rolls: int) -> int:
        assert 0 <= max_adjacent_paper_rolls <= 8
        max_neighbourhood_paper_rolls = max_adjacent_paper_rolls + 1
        # Reduce attribute lookups.
        tiles = self.tiles
        return sum(
            1 if (tiles[i] and tiles[i] <= max_neighbourhood_paper_rolls) else 0
            for i in self.indices
        )

    def mark_and_sweep_accessible_paper_rolls(self, max_adjacent_paper_rolls: int) -> int:
        assert 0 <= max_adjacent_paper_rolls <= 8
        accessible_paper_rolls = 0
        # Reduce attribute lookups.
        tiles = self.tiles
        kernel_offsets = self.kernel_offsets
        for i in self.indices:
            if tiles[i]:
                adjacent_paper_rolls = 0
                for kernel_i in kernel_offsets:
                    if tiles[i + kernel_i]:
                        adjacent_paper_rolls += 1
                if adjacent_paper_rolls <= max_adjacent_paper_rolls:
                    tiles[i] = 0
                    accessible_paper_rolls += 1
        return accessible_paper_rolls


########################################################################################################################
# Part 1
########################################################################################################################

MAX_ADJACENT_PAPER_ROLLS = 3


def count_accessible_paper_rolls(lines: Iterable[str]) -> int:
    """
    >>> count_accessible_paper_rolls([
    ...     '..@@.@@@@.',
    ...     '@@@.@.@.@@',
    ...     '@@@@@.@.@@',
    ...     '@.@@@@..@.',
    ...     '@@.@@@@.@@',
    ...     '.@@@@@@@.@',
    ...     '.@.@.@.@@@',
    ...     '@.@@@.@@@@',
    ...     '.@@@@@@@@.',
    ...     '@.@.@@@.@.',
    ... ])
    13
    """
    diagram = Diagram.from_lines(lines)
    diagram.mark_neighbourhood_paper_rolls()
    return diagram.count_accessible_paper_rolls(MAX_ADJACENT_PAPER_ROLLS)


########################################################################################################################
# Part 2
########################################################################################################################

def count_potentially_accessible_paper_rolls(lines: Iterable[str]) -> int:
    """
    >>> count_potentially_accessible_paper_rolls([
    ...     '..@@.@@@@.',
    ...     '@@@.@.@.@@',
    ...     '@@@@@.@.@@',
    ...     '@.@@@@..@.',
    ...     '@@.@@@@.@@',
    ...     '.@@@@@@@.@',
    ...     '.@.@.@.@@@',
    ...     '@.@@@.@@@@',
    ...     '.@@@@@@@@.',
    ...     '@.@.@@@.@.',
    ... ])
    43
    """
    diagram = Diagram.from_lines(lines)
    accessible_paper_rolls = 0
    while (newly_accessible_paper_rolls := diagram.mark_and_sweep_accessible_paper_rolls(MAX_ADJACENT_PAPER_ROLLS)):
        accessible_paper_rolls += newly_accessible_paper_rolls
    return accessible_paper_rolls


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
        print(count_accessible_paper_rolls(lines))
    elif args.part == 2:
        print(count_potentially_accessible_paper_rolls(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
