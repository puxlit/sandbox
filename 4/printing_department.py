#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable
from typing import NamedTuple


########################################################################################################################
# Diagram
########################################################################################################################

EMPTY_SPACE = '.'
PAPER_ROLL = '@'


def bake_adjacent_paper_rolls(rows: list[list[int]], width: int, height: int) -> None:
    for y in range(height):
        for x in range(width):
            if rows[y][x] >= 0:
                for kernel_y in range(max(0, y - 1), min(height, y + 2)):
                    for kernel_x in range(max(0, x - 1), min(width, x + 2)):
                        if (kernel_y == y) and (kernel_x == x):
                            continue
                        if rows[kernel_y][kernel_x] < 0:
                            continue
                        rows[kernel_y][kernel_x] += 1


class Diagram(NamedTuple):
    width: int
    height: int
    rows: tuple[tuple[int, ...], ...]

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'Diagram':
        width = -1
        rows: list[list[int]] = []
        for (y, line) in enumerate(lines):
            # Ensure width is consistent across lines.
            if y == 0:
                width = len(line)
            elif len(line) != width:
                raise ValueError(f'Width of line {y + 1} differs from line 1 ({len(line)} ≠ {width})')
            rows.append([{
                EMPTY_SPACE: -1,
                PAPER_ROLL: 0,
            }[char] for char in line])
        height = y + 1
        bake_adjacent_paper_rolls(rows, width, height)
        return Diagram(width, height, tuple(tuple(row) for row in rows))

    def count_accessible_paper_rolls(self, max_adjacent_paper_rolls: int) -> int:
        assert 0 <= max_adjacent_paper_rolls <= 8
        return sum(
            1 if (0 <= adjacent_paper_rolls <= max_adjacent_paper_rolls) else 0
            for row in self.rows
            for adjacent_paper_rolls in row
        )

    def prune(self, max_adjacent_paper_rolls: int) -> 'Diagram':
        rows = [[
            -1 if (adjacent_paper_rolls <= max_adjacent_paper_rolls) else 0
            for adjacent_paper_rolls in row
        ] for row in self.rows]
        bake_adjacent_paper_rolls(rows, self.width, self.height)
        return Diagram(self.width, self.height, tuple(tuple(row) for row in rows))


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
    return Diagram.from_lines(lines).count_accessible_paper_rolls(MAX_ADJACENT_PAPER_ROLLS)


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
    accessible_paper_rolls = diagram.count_accessible_paper_rolls(MAX_ADJACENT_PAPER_ROLLS)
    while (pruned_diagram := diagram.prune(MAX_ADJACENT_PAPER_ROLLS)) != diagram:
        accessible_paper_rolls += pruned_diagram.count_accessible_paper_rolls(MAX_ADJACENT_PAPER_ROLLS)
        diagram = pruned_diagram
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
