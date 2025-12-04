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


def bake_neighbourhood_paper_rolls(rows: list[list[int]], width: int, height: int) -> None:
    for y in range(1, height + 1):
        for x in range(1, width + 1):
            if rows[y][x]:
                neighbourhood_paper_rolls = 0
                for kernel_y in (y - 1, y, y + 1):
                    for kernel_x in (x - 1, x, x + 1):
                        if rows[kernel_y][kernel_x]:
                            neighbourhood_paper_rolls += 1
                rows[y][x] = neighbourhood_paper_rolls


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
                # Introduce top row of padding to reduce operations within `bake_neighbourhood_paper_rolls`.
                rows.append([0] * (width + 2))
            elif len(line) != width:
                raise ValueError(f'Width of line {y + 1} differs from line 1 ({len(line)} ≠ {width})')
            # Introduce left and right columns of padding to reduce operations within `bake_neighbourhood_paper_rolls`.
            rows.append([0, *({
                EMPTY_SPACE: 0,
                PAPER_ROLL: 1,
            }[char] for char in line), 0])
        # Introduce bottom row of padding to reduce operations within `bake_neighbourhood_paper_rolls`.
        rows.append([0] * (width + 2))
        height = y + 1
        bake_neighbourhood_paper_rolls(rows, width, height)
        return Diagram(width, height, tuple(tuple(row) for row in rows))

    def count_accessible_paper_rolls(self, max_adjacent_paper_rolls: int) -> int:
        assert 0 <= max_adjacent_paper_rolls <= 8
        max_neighbourhood_paper_rolls = max_adjacent_paper_rolls + 1
        return sum(
            1 if (neighbourhood_paper_rolls and neighbourhood_paper_rolls <= max_neighbourhood_paper_rolls) else 0
            for row in self.rows[1:-1]
            for neighbourhood_paper_rolls in row[1:-1]
        )

    def prune(self, max_adjacent_paper_rolls: int) -> 'Diagram':
        assert 0 <= max_adjacent_paper_rolls <= 8
        max_neighbourhood_paper_rolls = max_adjacent_paper_rolls + 1
        rows = [[
            1 if (neighbourhood_paper_rolls > max_neighbourhood_paper_rolls) else 0
            for neighbourhood_paper_rolls in row
        ] for row in self.rows]
        bake_neighbourhood_paper_rolls(rows, self.width, self.height)
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
