#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterable
from typing import NamedTuple


########################################################################################################################
# Part 1
########################################################################################################################

LETTER_TO_WORD_ORDINAL = {
    'X': 0,
    'M': 1,
    'A': 2,
    'S': 3,
}

WORD_LENGTH = len(LETTER_TO_WORD_ORDINAL)


class WordSearch(NamedTuple):
    width: int
    height: int
    rows: tuple[tuple[int, ...], ...]
    starting_word_positions: tuple[tuple[int, int], ...]

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> 'WordSearch':
        width = -1
        rows: list[tuple[int, ...]] = []
        starting_word_positions: list[tuple[int, int]] = []
        for (y, line) in enumerate(lines):
            # Ensure width is consistent across lines.
            if y == 0:
                width = len(line)
            elif len(line) != width:
                raise ValueError(f'Width of line {y + 1} differs from line 1 ({len(line)} ≠ {width})')
            row = tuple(LETTER_TO_WORD_ORDINAL[letter] for letter in line)
            rows.append(row)
            starting_word_positions.extend((x, y) for (x, i) in enumerate(row) if i == 0)
        height = y + 1
        return WordSearch(width, height, tuple(rows), tuple(starting_word_positions))

    def count_occurrences_from_position(self, x: int, y: int) -> int:
        return sum((
            self.check_position_and_radial(x, y, 1, 0),    # rightwards
            self.check_position_and_radial(x, y, 1, 1),    # diagonally to the bottom-right
            self.check_position_and_radial(x, y, 0, 1),    # downwards
            self.check_position_and_radial(x, y, -1, 1),   # diagonally to the bottom-left
            self.check_position_and_radial(x, y, -1, 0),   # leftwards
            self.check_position_and_radial(x, y, -1, -1),  # diagonally to the top-left
            self.check_position_and_radial(x, y, 0, -1),   # upwards
            self.check_position_and_radial(x, y, 1, -1),   # diagonally to the top-right
        ))

    def check_position_and_radial(self, x: int, y: int, x_delta: int, y_delta: int) -> bool:
        # Bounds check
        assert (0 <= x < self.width) and (0 <= y < self.height)
        if not 0 <= (x + (x_delta * (WORD_LENGTH - 1))) < self.width:
            return False
        if not 0 <= (y + (y_delta * (WORD_LENGTH - 1))) < self.height:
            return False
        for i in range(WORD_LENGTH):
            if self.rows[y][x] != i:
                return False
            x += x_delta
            y += y_delta
        return True


def count_occurrences(lines: Iterable[str]) -> int:
    """
    >>> count_occurrences([
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
    return sum(word_search.count_occurrences_from_position(x, y) for (x, y) in word_search.starting_word_positions)


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
        print(count_occurrences(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
