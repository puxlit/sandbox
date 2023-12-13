#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from collections.abc import Iterator
from itertools import chain, combinations
from typing import NamedTuple


########################################################################################################################
# Notes
########################################################################################################################

def single_bit_diff_position(a: int, b: int) -> int:
    x = a ^ b
    if x == 0:
        # Inputs are identical.
        return -1
    if x & (x - 1) != 0:
        # XORed inputs is not a power of two; multiple bits are set.
        return -1
    i = -1
    while x:
        x >>= 1
        i += 1
    return i


ASH = '.'
ROCKS = '#'

COLUMN_REFLECTION_SUMMARY_FACTOR = 1
ROW_REFLECTION_SUMMARY_FACTOR = 100


class Pattern(NamedTuple):
    width: int
    height: int
    columns: tuple[int, ...] = ()
    rows: tuple[int, ...] = ()

    @classmethod
    def from_lines(cls, lines: Iterator[str]) -> 'Pattern':
        width = -1
        height = 0
        columns: list[int] = []
        rows: list[int] = []
        for (y, line) in enumerate(lines):
            # Ensure width is consistent across lines.
            if y == 0:
                width = len(line)
                assert not columns
                columns = [0] * width
            elif len(line) == 0:
                break
            elif len(line) != width:
                raise ValueError(f'Width of line {y + 1} differs from line 1 ({len(line)} ≠ {width})')

            height += 1
            row = 0
            for (x, char) in enumerate(line):
                assert char in {ASH, ROCKS}
                bit = char == ROCKS
                columns[x] = (columns[x] << 1) | bit
                row = (row << 1) | bit
            rows.append(row)
        return Pattern(width, height, tuple(columns), tuple(rows))

    def summarise(self, ignore_summary: int = 0) -> int:
        """
        >>> Pattern.from_lines(iter([
        ...     '#.##..##.',
        ...     '..#.##.#.',
        ...     '##......#',
        ...     '##......#',
        ...     '..#.##.#.',
        ...     '..##..##.',
        ...     '#.#.##.#.',
        ... ])).summarise()
        5
        >>> Pattern.from_lines(iter([
        ...     '#...##..#',
        ...     '#....#..#',
        ...     '..##..###',
        ...     '#####.##.',
        ...     '#####.##.',
        ...     '..##..###',
        ...     '#....#..#',
        ... ])).summarise()
        400

        >>> Pattern.from_lines(iter([
        ...     '#..###.##.#.#...#',
        ...     '#.##.....#.###.#.',
        ...     '#.##..#.###.#.#.#',
        ...     '##........#..###.',
        ...     '#..##.#.###..#.#.',
        ...     '#..#.#...#....##.',
        ...     '#..#.#...#....##.',
        ...     '#..##.#.###..#.#.',
        ...     '##........#..###.',
        ...     '#.##..#.###.#.#.#',
        ...     '#.##.....#.###.#.',
        ...     '#..###.##...#...#',
        ...     '.##...##..#..##..',
        ...     '####.#...#...##..',
        ...     '..##.#..#..#.#.#.',
        ...     '##.##.#.#..#.#..#',
        ...     '##.##.#.#..#.#..#',
        ... ])).summarise()
        1600
        """
        best_reflection_length = 0
        best_summary = 0
        for x in range(0, self.width - 1):
            if self.columns[x] != self.columns[x + 1]:
                continue
            reflection_length = min(x + 1, self.width - x - 1)
            if reflection_length <= best_reflection_length:
                continue
            if tuple(reversed(self.columns[x + 1 - reflection_length:x + 1])) != self.columns[x + 1:x + 1 + reflection_length]:
                continue
            summary = COLUMN_REFLECTION_SUMMARY_FACTOR * (x + 1)
            if summary != ignore_summary:
                best_reflection_length = reflection_length
                best_summary = summary
        for y in range(0, self.height - 1):
            if self.rows[y] != self.rows[y + 1]:
                continue
            reflection_length = min(y + 1, self.height - y - 1)
            if reflection_length <= best_reflection_length:
                continue
            if tuple(reversed(self.rows[y + 1 - reflection_length:y + 1])) != self.rows[y + 1:y + 1 + reflection_length]:
                continue
            summary = ROW_REFLECTION_SUMMARY_FACTOR * (y + 1)
            if summary != ignore_summary:
                best_reflection_length = reflection_length
                best_summary = summary
        return best_summary

    def flip_bit(self, x: int, y: int) -> 'Pattern':
        assert 0 <= x <= self.width
        assert 0 <= y <= self.height
        modified_column = self.columns[x] ^ (1 << y)
        modified_columns = self.columns[:x] + (modified_column,) + self.columns[x + 1:]
        modified_row = self.rows[y] ^ (1 << x)
        modified_rows = self.rows[:y] + (modified_row,) + self.rows[y + 1:]
        return Pattern(self.width, self.height, modified_columns, modified_rows)

    def summarise_repaired(self) -> int:
        """
        >>> Pattern.from_lines(iter([
        ...     '#.##..##.',
        ...     '..#.##.#.',
        ...     '##......#',
        ...     '##......#',
        ...     '..#.##.#.',
        ...     '..##..##.',
        ...     '#.#.##.#.',
        ... ])).summarise_repaired()
        300
        >>> Pattern.from_lines(iter([
        ...     '#...##..#',
        ...     '#....#..#',
        ...     '..##..###',
        ...     '#####.##.',
        ...     '#####.##.',
        ...     '..##..###',
        ...     '#....#..#',
        ... ])).summarise_repaired()
        100
        """
        smudged_summary = self.summarise()
        for ((i_0, column_0), (i_1, column_1)) in combinations(enumerate(self.columns), 2):
            bit_diff_position = single_bit_diff_position(column_0, column_1)
            if bit_diff_position < 0:
                continue
            modified_pattern = self.flip_bit(i_0, bit_diff_position)
            new_summary = modified_pattern.summarise(ignore_summary=smudged_summary)
            if new_summary > 0:
                return new_summary
        for ((i_0, row_0), (i_1, row_1)) in combinations(enumerate(self.rows), 2):
            bit_diff_position = single_bit_diff_position(row_0, row_1)
            if bit_diff_position < 0:
                continue
            modified_pattern = self.flip_bit(bit_diff_position, i_0)
            new_summary = modified_pattern.summarise(ignore_summary=smudged_summary)
            if new_summary > 0:
                return new_summary
        return 0


########################################################################################################################
# Part 1
########################################################################################################################

def patterns_from_lines(lines: Iterator[str]) -> Iterator[Pattern]:
    while True:
        try:
            line = next(lines)
        except StopIteration:
            return
        yield Pattern.from_lines(chain.from_iterable(((line,), lines)))


def summarise_notes(lines: Iterator[str]) -> int:
    """
    >>> summarise_notes(iter([
    ...     '#.##..##.',
    ...     '..#.##.#.',
    ...     '##......#',
    ...     '##......#',
    ...     '..#.##.#.',
    ...     '..##..##.',
    ...     '#.#.##.#.',
    ...     '',
    ...     '#...##..#',
    ...     '#....#..#',
    ...     '..##..###',
    ...     '#####.##.',
    ...     '#####.##.',
    ...     '..##..###',
    ...     '#....#..#',
    ... ]))
    405
    """
    patterns = patterns_from_lines(lines)
    return sum(pattern.summarise() for pattern in patterns)


########################################################################################################################
# Part 2
########################################################################################################################

def summarise_repaired_notes(lines: Iterator[str]) -> int:
    """
    >>> summarise_repaired_notes(iter([
    ...     '#.##..##.',
    ...     '..#.##.#.',
    ...     '##......#',
    ...     '##......#',
    ...     '..#.##.#.',
    ...     '..##..##.',
    ...     '#.#.##.#.',
    ...     '',
    ...     '#...##..#',
    ...     '#....#..#',
    ...     '..##..###',
    ...     '#####.##.',
    ...     '#####.##.',
    ...     '..##..###',
    ...     '#....#..#',
    ... ]))
    400
    """
    patterns = patterns_from_lines(lines)
    return sum(pattern.summarise_repaired() for pattern in patterns)


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
        print(summarise_notes(lines))
    elif args.part == 2:
        print(summarise_repaired_notes(lines))
    else:
        raise ValueError(f'{args.part} is not a valid part')


if __name__ == '__main__':
    main()
