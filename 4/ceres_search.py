#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable
from typing import NamedTuple


########################################################################################################################
# Word search
########################################################################################################################

X_BITMASK = 1
M_BITMASK = 2
A_BITMASK = 4
S_BITMASK = 8
MS_BITMASK = M_BITMASK | S_BITMASK

LETTER_TO_BITMASK = {
    'X': X_BITMASK,
    'M': M_BITMASK,
    'A': A_BITMASK,
    'S': S_BITMASK,
}

WORD_LENGTH = len(LETTER_TO_BITMASK)


class WordSearch(NamedTuple):
    width: int
    height: int
    rows: tuple[tuple[int, ...], ...]
    starting_xs: tuple[tuple[int, int], ...]
    starting_as: tuple[tuple[int, int], ...]

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'WordSearch':
        width = -1
        rows: list[tuple[int, ...]] = []
        starting_xs: list[tuple[int, int]] = []
        starting_as: list[tuple[int, int]] = []
        for (y, line) in enumerate(lines):
            # Ensure width is consistent across lines.
            if y == 0:
                width = len(line)
            elif len(line) != width:
                raise ValueError(f'Width of line {y + 1} differs from line 1 ({len(line)} ≠ {width})')
            row = tuple(LETTER_TO_BITMASK[letter] for letter in line)
            rows.append(row)
            starting_xs.extend((x, y) for (x, i) in enumerate(row) if i == X_BITMASK)
            starting_as.extend((x, y) for (x, i) in enumerate(row) if i == A_BITMASK)
        height = y + 1
        return WordSearch(width, height, tuple(rows), tuple(starting_xs), tuple(starting_as))

    def count_xmas_occurrences_at_position(self, x: int, y: int) -> int:
        return sum((
            self.check_xmas_at_position_and_radial(x, y, 1, 0),    # rightwards
            self.check_xmas_at_position_and_radial(x, y, 1, 1),    # diagonally to the bottom-right
            self.check_xmas_at_position_and_radial(x, y, 0, 1),    # downwards
            self.check_xmas_at_position_and_radial(x, y, -1, 1),   # diagonally to the bottom-left
            self.check_xmas_at_position_and_radial(x, y, -1, 0),   # leftwards
            self.check_xmas_at_position_and_radial(x, y, -1, -1),  # diagonally to the top-left
            self.check_xmas_at_position_and_radial(x, y, 0, -1),   # upwards
            self.check_xmas_at_position_and_radial(x, y, 1, -1),   # diagonally to the top-right
        ))

    def check_xmas_at_position_and_radial(self, x: int, y: int, x_delta: int, y_delta: int) -> bool:
        # Bounds check
        assert (0 <= x < self.width) and (0 <= y < self.height)
        if not 0 <= (x + (x_delta * (WORD_LENGTH - 1))) < self.width:
            return False
        if not 0 <= (y + (y_delta * (WORD_LENGTH - 1))) < self.height:
            return False
        for i in range(WORD_LENGTH):
            if self.rows[y][x] != (1 << i):
                return False
            x += x_delta
            y += y_delta
        return True

    def check_crossed_mas_at_position(self, x: int, y: int) -> bool:
        # Bounds check
        if not (1 <= x < (self.width - 1)):
            return False
        if not (1 <= y < (self.height - 1)):
            return False
        # Check we actually have an 'A'.
        if self.rows[y][x] != A_BITMASK:
            return False
        # Check top-left to bottom-right diagonal.
        if (self.rows[y - 1][x - 1] | self.rows[y + 1][x + 1]) != MS_BITMASK:
            return False
        # Check bottom-left to top-right diagonal.
        if (self.rows[y + 1][x - 1] | self.rows[y - 1][x + 1]) != MS_BITMASK:
            return False
        return True


########################################################################################################################
# Part 1
########################################################################################################################

def count_xmas_occurrences(lines: Iterable[str]) -> int:
    """
    >>> count_xmas_occurrences([
    ...    'MMMSXXMASM',
    ...    'MSAMXMSMSA',
    ...    'AMXSXMAAMM',
    ...    'MSAMASMSMX',
    ...    'XMASAMXAMM',
    ...    'XXAMMXXAMA',
    ...    'SMSMSASXSS',
    ...    'SAXAMASAAA',
    ...    'MAMMMXMMMM',
    ...    'MXMXAXMASX',
    ... ])
    18
    """
    word_search = WordSearch.from_lines(lines)
    return sum(word_search.count_xmas_occurrences_at_position(x, y) for (x, y) in word_search.starting_xs)


########################################################################################################################
# Part 2
########################################################################################################################

def count_crossed_mas_occurrences(lines: Iterable[str]) -> int:
    """
    >>> count_crossed_mas_occurrences([
    ...    'MMMSXXMASM',
    ...    'MSAMXMSMSA',
    ...    'AMXSXMAAMM',
    ...    'MSAMASMSMX',
    ...    'XMASAMXAMM',
    ...    'XXAMMXXAMA',
    ...    'SMSMSASXSS',
    ...    'SAXAMASAAA',
    ...    'MAMMMXMMMM',
    ...    'MXMXAXMASX',
    ... ])
    9
    """
    word_search = WordSearch.from_lines(lines)
    return sum(word_search.check_crossed_mas_at_position(x, y) for (x, y) in word_search.starting_as)


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
        print(count_xmas_occurrences(lines))
    elif args.part == 2:
        print(count_crossed_mas_occurrences(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
